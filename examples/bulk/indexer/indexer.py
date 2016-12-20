#!/usr/bin/env python3
import argparse
import subprocess
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class IndexingHandler(FileSystemEventHandler):

    def __init__(self, elastic):
        super().__init__()
        self.elastic = elastic

    def _do_indexing(self, urlfile):
        print('got new urlfile: {}'.format(urlfile))
        p1 = subprocess.Popen(['./bulk.py', '--infile', urlfile],
                              stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['./elastic.py', '--elastic', self.elastic],
                              stdin=p1.stdout)
        p2.communicate()

    def on_created(self, event):
        self._do_indexing(event.src_path)

    def on_moved(self, event):
        self._do_indexing(event.dest_path)

    def on_modified(self, event):
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

    args = parser.parse_args()
    run(args.watchdir, args.elastic)
