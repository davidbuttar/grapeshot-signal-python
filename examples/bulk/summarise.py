#!/usr/bin/env python3
import argparse
import operator
import io
import sys
import json
import collections


class Summariser:

    def __init__(self, keyname, title):
        self.summary = collections.defaultdict(int)
        self.keyname = keyname
        self.title = title

    def increment(self, data):
        val = data.get(self.keyname)
        self.summary[str(val)] += 1
        return val

    def tabulate(self):
        total = sum(self.summary.values())
        table = sorted(self.summary.items(),
                       key=operator.itemgetter(1),
                       reverse=True)
        return {'title': self.title,
                'total': total,
                'table': table}


def summarise(infile, outfile):
    status_code_summary = Summariser('status_code', "Status Codes")
    language_summary = Summariser('language', "Languages")
    segment_summary = Summariser('name', "Segments")
    status_summary = Summariser('status', "Statuses")
    error_summary = Summariser('error_code', "Errors")
    categories_keywords_summary = collections.defaultdict(
        lambda: collections.defaultdict(int))

    with infile as f:
        for line in f:
            data = json.loads(line)
            has_status_code = status_code_summary.increment(data)
            result = data['result']
            if not has_status_code:
                # only get status code for api errors
                status = status_summary.increment(result)
                if status == 'ok':
                    language_summary.increment(result)
                    segments = result['segments']
                    for segment in segments:
                        name = segment_summary.increment(segment)
                        for matchterm in segment['matchterms']:
                            categories_keywords_summary[name][matchterm] += 1
                elif status == 'error':
                    error_summary.increment(result)

    for summary in (status_code_summary,
                    language_summary,
                    segment_summary,
                    status_summary,
                    error_summary):
        print(summary.tabulate(), file=outfile)

    # print(tabulate(categories_keywords_summary, "Category matchterms"),
    #      outfile=outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--infile", nargs="?",
                        help="file containing json results",
                        type=argparse.FileType('r'), default=sys.stdin)

    parser.add_argument("--outfile", nargs="?",
                        help="output file, defaults to stdout",
                        type=argparse.FileType('w'),
                        default=sys.stdout)

    args = parser.parse_args()
    summarise(args.infile, args.outfile)
