#!/usr/bin/env python3

# Uses async/await and type annotations -> needs python 3.5
import argparse
import asyncio
import logging
import concurrent
import functools
import collections
import os
import time
from grapeshot_signal import SignalClient, SignalModel, rels,\
    APIError, OverQuotaError, RateLimitError, config
import tqdm
import json
from utils import line_count


print(config.api_host)

logger = logging.getLogger()


class UrlData(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, url, lineno, try_count=0, result=None,
                 request_time=0, response_time=0):
        '''
         Args:
            url: read from input
            lineno: line number from input (0 based)
            try_count: number of times url has been tried
                       (retried if 429 response)
            result: result of the call either SignalModel or some exception
                    (429s are retried)
            request_time: time stamp when the call was made (approx)
            response_time: time stamp when response received (approx)
        '''
        self.url = url
        self.lineno = lineno
        self.try_count = try_count
        self.result = result
        self.request_time = request_time
        self.response_time = response_time

    def prepare(self):
        '''change values of self suitable for json output'''

        if isinstance(self.result, Exception):
            if isinstance(self.result, (APIError, RateLimitError)):
                self.status_code = self.result.status_code()
                self.result = str(self.result)

        elif isinstance(self.result, SignalModel):

            if self.result.is_ok():
                self.result = self.result.get_embedded(rels.segments)
                # rewrite the matchterms for each segment to just be a list of terms
                for segment in self.result['segments']:
                    terms = segment['matchterms']
                    # sometimes we produce an empty "term"
                    segment['matchterms'] = [t.get('name', '') for t in terms]

            elif self.result.is_queued():
                del(self.result['_embedded'])

            # we already have these already, or can look them up
            for key in ('url', '_links', 'error_message'):
                if key in self.result:
                    del(self.result[key])

        else:
            self.result = 'Unexpected result'


END_OF_INPUT = UrlData('', -1)



async def write_result(url_data, of):
    '''output result to `of`, which should be a writable file

    '''
    url_data.prepare()
    json.dump(url_data, of)
    of.write(os.linesep)


def get_page(client, url_data):
    url_data.request_time = time.time()
    url_data.try_count += 1
    try:
        page = client.get_page(url_data.url, [rels.segments])
    except Exception as e:
        # we catch all exceptions and deal with them
        page = e
    url_data.response_time = time.time()
    url_data.result = page
    return url_data


async def consume_urls(executor, inqueue: asyncio.Queue, unlimited: asyncio.Event,
                       of, client, retry429, pause429):
    loop = asyncio.get_event_loop()
    while True:
        url_data = await inqueue.get()

        if url_data is END_OF_INPUT:
            await inqueue.put(END_OF_INPUT)  # so other consumers will exit
            break

        if pause429:
            await unlimited.wait()

        future = loop.run_in_executor(executor, get_page, client, url_data)
        await future
        result = url_data.result

        if isinstance(result, RateLimitError):

            if pause429:
                unlimited.clear()
                await asyncio.sleep(result.retry_after())
                unlimited.set()

            if retry429:
                await inqueue.put(url_data)
            else:
                await write_result(url_data, of)

        elif isinstance(result, KeyboardInterrupt):
            raise
        else:
            if isinstance(result, OverQuotaError):
                # no point in continuing if we're over quota
                break

            await write_result(url_data, of)


def url_line(lineno, line):
    return UrlData(line, lineno)


def queued_json_lines(lineno, line):
    json_string = line.strip()
    json_data = json.loads(json_string)
    result = json_data.get('result')
    if result:
        # result can be a string for error - should fix that
        if isinstance(result, str):
            return None
        status = result.get('status')
        if status == 'queued':
            url = json_data['url']
            return UrlData(url, lineno)
    return None


async def produce_urls(queue: asyncio.Queue, urlfile, pbar,
                       line_processor=url_line):

    with open(urlfile) as f:
        for i, line in enumerate(f):
            il = line_processor(i, line.strip())
            if il:
                # don't want to copy the whole file to the queue, since it
                # could be large, the queue has a limited size
                await queue.put(il)
            pbar.update(1)
    await queue.put(END_OF_INPUT)


def run(urlfile, key: str, lineproc,
        count: int, outfile, retry429, pause429):
    line_processor = {'urlline': url_line,
                      'queued': queued_json_lines}[lineproc]
    if not key:
        key = config.api_key
    inqueue = asyncio.Queue(count*3)
    client = SignalClient(key)
    loop = asyncio.get_event_loop()
    lines = line_count(urlfile)
    pbar = tqdm.tqdm(total=lines)
    limit = asyncio.Event()
    limit.set()  # is this the state on creation?
    with open(outfile, 'w') as of:
        with concurrent.futures.ThreadPoolExecutor(count) as executor:
            # we could make the writing the results via coroutines, but the
            # time taken for that is likely to be small compared to the api
            # calls, so probably doesn't make much different. Possibly if
            # output file is on a network drive...
            loop.run_until_complete(
                asyncio.gather(
                    produce_urls(inqueue, urlfile, pbar, line_processor),
                    *(consume_urls(executor, inqueue, limit, of, client, retry429, pause429)
                      for i in range(count))
                ))

    pbar.close()


def main():
    # logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Make multiple requests to the Grapeshot OpenAPI server.'
    )

    parser.add_argument("infile", nargs="?",
                        help="file containing one url per line")

    parser.add_argument("--apikey", help="api key for the api server",
                        default="")

    # at some point more consumers will not help, but if there's a lot of idle
    # waiting for repsonses it may do. Note that in any case we can't make more
    # requests that the server's rate limiting strategy allows.
    parser.add_argument("--consumers",
                        help="number of url consumers",
                        default=10,
                        type=int)
    parser.add_argument("--outfile",
                        help="file containing results")
    parser.add_argument("--errors-file",
                        help="file containing errors")

    parser.add_argument("--retry429",
                        help="retry rate limited requests",
                        dest="retry429",
                        action="store_true")
    parser.add_argument("--no-retry429",
                        help="retry rate limited requests",
                        dest="retry429",
                        action="store_false")

    parser.add_argument(
        "--lineparse",
        help='strategy used to parse input lines. Either "urlline" or "queued"',
        default='urlline')

    parser.add_argument("--pause429",
                        help="pause on 429",
                        dest="pause429",
                        action="store_true")
    parser.add_argument("--no-pause429",
                        help="pause on 429",
                        dest="pause429",
                        action="store_false")

    parser.set_defaults(retry429=True, pause429=True)

    args = parser.parse_args()
    run(args.infile, args.apikey, args.lineparse, args.consumers,
        args.outfile, args.retry429, args.retry429)


if __name__ == '__main__':
    main()
