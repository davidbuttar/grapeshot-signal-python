#!/bin/env python3

# Uses async/await and type annotations -> needs python 3.5
import aiofiles
import argparse
import asyncio
import itertools
import logging
import sys
import concurrent

from grapeshot_signal import SignalClient, APIError, OverQuotaError, rels

logger = logging.getLogger()

def get_page(client, url):
    try:
        page = client.get_page(url, [rels.segments])
    except Exception as e:
        page = e
    print(page)

async def consume_urls(queue, client, count):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=count) as executor:
        url = await queue.get()
        while url is not None:
            loop.run_in_executor(executor, get_page, client, url)
            url = await queue.get()

async def produce_urls(queue, urlfile):
    with open(urlfile) as f:
        for line in f:
            url = line.strip()
            await queue.put(url)
    await queue.put(None)

def run(urlfile, key: str, count: int):
    queue = asyncio.Queue(count)
    client = SignalClient(key)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(*[
            produce_urls(queue, urlfile),
            consume_urls(queue, client, count)
        ]))

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='Make multiple requests to the Grapeshot OpenAPI server.'
    )
    parser.add_argument("apikey", help="api key for the api server")

    parser.add_argument("urlfile", nargs="?",
                        help="file containing one url per line")

    # at some point more consumers will not help, but if there's a lot of idle
    # waiting for repsonses it may do. Note that in any case we can't make more
    # requests that the server's rate limiting strategy allows.
    parser.add_argument("--consumers",
                        help="number of url consumers",
                        default=10,
                        type=int)

    args = parser.parse_args()
    run(args.urlfile, args.apikey, args.consumers)



if __name__ == '__main__':
    main()
