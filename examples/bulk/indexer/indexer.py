#!/usr/bin/env python3
import argparse
import subprocess
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class IndexingHandler(FileSystemEventHandler):

    def __init__(self, elastic):
        super().__init__()
        self.elastic = elastic

    def _do_indexing(self, urlfile):
        logging.debug('got new urlfile: {}'.format(urlfile))
        p1 = subprocess.Popen(['./bulk.py', '--infile', urlfile],
                              stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['./elastic.py', '--elastic', self.elastic],
                              stdin=p1.stdout)
        p2.communicate()

    def _log_event(self, method_name, event):
        logging.debug('on_created event: {}'.format(str(event)))

    def on_created(self, event):
        self._log_event('on_created', event)
        self._do_indexing(event.src_path)

    def on_moved(self, event):
        self._log_event('on_moved', event)
        self._do_indexing(event.dest_path)

    def on_modified(self, event):
        self._log_event('on_modified', event)
        self._do_indexing(event.src_path)


def run(watchdir, elastic):
    '''watches watchdir for new files, uses their contents to create a new index
    in elasticsearch
    '''
    observer = Observer()
    handler = IndexingHandler(elastic)
    observer.schedule(handler, watchdir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("watchdir", help="directory for urlfiles")
    parser.add_argument(
        "--elastic", nargs="?",
        help="url for elastic, defaults to http://localhost:9200",
        default='http://localhost:9200')
    parser.add_argument(
        "--log", help="log level",
        dest="logLevel",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    )
    args = parser.parse_args()
    if args.logLevel:
        logging.basicConfig(level=getattr(logging, args.logLevel))
    run(args.watchdir, args.elastic)
