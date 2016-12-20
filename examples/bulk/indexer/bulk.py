#!/usr/bin/env python3

# Uses async/await and type annotations -> needs python 3.5
import argparse
import asyncio
import concurrent
import functools
import collections
import os
import sys
import datetime
from grapeshot_signal import SignalClient, SignalModel, rels,\
    APIError, OverQuotaError, config
import tqdm
import json
from utils import line_count


class UrlData(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, url, client_id, try_count=0, result=None,
                 request_time=0, response_time=0):
        '''
         Args:
            url: read from input
            client_id: client identifier
            try_count: number of times url has been tried
            result: result of the signal api call
            request_time: time stamp when the call was made (approx)
            response_time: time stamp when response received (approx)
        '''
        self.url = url
        self.client_id = client_id
        self.try_count = try_count
        self.result = result
        self.request_time = request_time
        self.response_time = response_time

    def prepare(self):
        '''Destructively change self in preparation for json output.
        '''

        if isinstance(self.result, Exception):
            if isinstance(self.result, APIError):
                self.status_code = self.result.status_code()
                self.result = {"message": str(self.result)}

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

    async def write_json(self, of, newline=True):
        '''Write a json representation to `of`, which should be quack like
          a writable file. If `newline` tests true, write a newline at the end.
        '''
        self.prepare()
        json.dump(self, of)
        if newline:
            of.write(os.linesep)

END_OF_INPUT = None


def get_page(client, url_data):
    url_data.request_time = datetime.datetime.utcnow().isoformat()
    url_data.try_count += 1
    try:
        page = client.get_page(url_data.url, [rels.segments])
    except Exception as e:
        # we catch all exceptions and deal with them
        page = e
    url_data.response_time = datetime.datetime.utcnow().isoformat()
    url_data.result = page
    return url_data


async def consume_urls(executor,
                       inqueue: asyncio.Queue, of, client, retry429, pause429):
    loop = asyncio.get_event_loop()
    unlimited = asyncio.Event()
    unlimited.set()

    while True:
        url_data = await inqueue.get()

        if url_data is END_OF_INPUT:
            await inqueue.put(END_OF_INPUT)  # so other consumers will exit
            break

        if pause429:
            await unlimited.wait()

        await loop.run_in_executor(executor, get_page, client, url_data)

        result = url_data.result

        if isinstance(result, APIError):
            if result.status_code() == 429:

                if pause429:
                    unlimited.clear()
                    await asyncio.sleep(result.retry_after())
                    unlimited.set()

                if retry429:
                    await inqueue.put(url_data)
                    continue

        elif isinstance(result, OverQuotaError):
            # no point in continuing if we're over quota
            break

        elif isinstance(result, Exception):
            raise result

        await url_data.write_json(of)


def url_line(lineno, line):
    '''create UrlData from `line`
    '''
    return UrlData(line, lineno)


async def produce_urls(queue: asyncio.Queue, urlfile,
                       line_processor=url_line, report_progress=True):
    '''call `line_processor` on each line of `urlfile`; put the result on `queue`
       if it tests True.  If `report_progress` tests True, print a graphical
       progress bar.

    '''
    if report_progress:
        lines = line_count(urlfile)
        pbar = tqdm.tqdm(total=lines)

    with urlfile as f:
        for i, line in enumerate(f):
            il = line_processor(i, line.strip())
            if il:
                # don't want to copy the whole file to the queue, since it
                # could be large, the queue has a limited size
                await queue.put(il)
            if report_progress:
                pbar.update(1)

    await queue.put(END_OF_INPUT)
    if report_progress:
        pbar.close()


def run(urlfile, key: str, count: int, outfile, retry429, pause429):
    if not key:
        key = config.api_key

    # queue size is a guess.
    inqueue = asyncio.Queue(count*3)

    client = SignalClient(key)
    loop = asyncio.get_event_loop()

    # Maybe more threads is better, but rate limiting will provide an upper
    # bound on throughput in any case.

    with concurrent.futures.ThreadPoolExecutor(count) as executor:
        producer = produce_urls(inqueue, urlfile)
        consumers = (consume_urls(
            executor, inqueue, outfile, client, retry429, pause429)
                     for i in range(count))

        loop.run_until_complete(asyncio.gather(producer, *consumers))


def process_command_line()
    parser = argparse.ArgumentParser(
        description='Make multiple requests to the Grapeshot OpenAPI server.'
    )

    parser.add_argument("--infile", nargs="?",
                        help="file containing one url per line, defaults to stdin",
                        type=argparse.FileType('r'), default=sys.stdin)

    parser.add_argument("--outfile", nargs="?",
                        help="file containing results, defaults to stdout",
                        type=argparse.FileType('w'),
                        default=sys.stdout)

    parser.add_argument("--apikey", help="api key for the api server",
                        default="")

    # at some point more consumers will not help, but if there's a lot of idle
    # waiting for repsonses it may do. In any case we can't make faster
    # requests than server side rate limiting allows.
    parser.add_argument("--consumers",
                        help="number of url consumers",
                        default=35,
                        type=int)

    parser.add_argument("--retry429",
                        help="retry rate limited requests",
                        dest="retry429",
                        action="store_true")

    parser.add_argument("--no-retry429",
                        help="do not retry rate limited requests",
                        dest="retry429",
                        action="store_false")

    parser.add_argument("--pause429",
                        help="pause on 429",
                        dest="pause429",
                        action="store_true")
    parser.add_argument("--no-pause429",
                        help="do not pause on 429, not recommended - just for testing",
                        dest="pause429",
                        action="store_false")

    parser.set_defaults(retry429=True, pause429=True)

    return parser.parse_args()


def main():
    args = process_command_line()
    run(args.infile, args.apikey, args.consumers,
        args.outfile, args.retry429, args.retry429)


if __name__ == '__main__':
    main()
