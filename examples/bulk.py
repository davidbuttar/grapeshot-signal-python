#!/usr/bin/env python3

# Uses async/await and type annotations -> needs python 3.5
import argparse
import asyncio
import logging
import concurrent
import functools
from grapeshot_signal import SignalClient, APIError, OverQuotaError, RateLimitError, rels

logger = logging.getLogger()


def get_page(client, url):
    try:
        page = client.get_page(url, [rels.segments])
    except Exception as e:
        page = e
    return page


def write_result(result, of):
    '''Deal with the result, which is either a SignalModel (for successful calls); or APIError
    '''
    of.write(str(result))

def get_page_callback(throttled, stopping, url, of, future):
    # no need to test if done, because only called once done
    result = future.result()

    if isinstance(result, RateLimitError):
        # If we're rate limited we wait according to the "Retry-After"
        # header. This is controlled through the `throttled`
        # queue. consume_urls will wait for this queue if it's non-empty and
        # sleep for the retry period before moving the throttled urls to the
        # main queue
        throttled.put((url, result.retry_after()))
    elif isinstance(result, OverQuotaError):
        # no point in continuing if we're overquota
        stopping[0] = True
        # still record the error
        write_result(result, of)
    else:
        write_result(result, of)



async def consume_urls(inqueue: asyncio.Queue, of, client, count):
    loop = asyncio.get_event_loop()
    throttled = asyncio.Queue()
    stopping = (False,)
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as executor:
        url = await inqueue.get()
        while (url is not None) and (not stopping[0]):
            if not throttled.empty():
                throttled_url, retry = throttled.get_nowait()
                asyncio.sleep(retry)
                inqueue.push(throttled_url)
                while not throttled.empty():
                    await inqueue.put(throttled.get_nowait()[0])
            future = loop.run_in_executor(executor, get_page, client, url)
            future.add_done_callback(
                functools.partial(get_page_callback, throttled, stopping, url, of))
            url = await inqueue.get()


async def produce_urls(queue, urlfile):
    with open(urlfile) as f:
        for line in f:
            url = line.strip()
            await queue.put(url)
    await queue.put(None)


def run(urlfile, key: str, count: int, outfile):
    inqueue = asyncio.Queue(count)
    client = SignalClient(key)
    loop = asyncio.get_event_loop()
    with open(outfile, 'w') as of:

        loop.run_until_complete(
            asyncio.gather(*[
                produce_urls(inqueue, urlfile),
                consume_urls(inqueue, of, client, count)
            ]))


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Make multiple requests to the Grapeshot OpenAPI server.'
    )
    parser.add_argument("apikey", help="api key for the api server")

    parser.add_argument("infile", nargs="?",
                        help="file containing one url per line")

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

    args = parser.parse_args()
    run(args.infile, args.apikey, args.consumers, args.outfile)


if __name__ == '__main__':
    main()
