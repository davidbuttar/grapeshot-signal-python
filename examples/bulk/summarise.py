#!/usr/bin/env python3
import sys
import json
import collections
import tqdm
from utils import line_count


# results are either api errors (i.e. bad calls - nothing returned), in which
# case we have a status code.

# Otherwise results are api results, which have a status (which we count) if
# the status is error there's nothing more. Otherwise we count the language and
# each of the segments in the result.


def increment_key(data_in, summary, key):
    val = data_in.get(key)
    if val is not None:
        summary[str(val)] += 1
        return True
    return False


def print_summary(summary, total):
    total = 0
    for (k, v) in summary.items():
        total += v
        print('{}\t\t{}\t\t{}%'.format(k, v, 100 * v/total))

    print()
    print('aggregate: {}'.format(total))
    print()


def summarise(infile):
    lines = line_count(infile)
    pbar = tqdm.tqdm(total=lines)
    language_summary = collections.defaultdict(int)
    segment_summary = collections.defaultdict(int)
    status_code_summary = collections.defaultdict(int)
    status_summary = collections.defaultdict(int)
    with open(infile) as f:
        for line in f:
            json_data = json.loads(line)
            if not increment_key(json_data, status_code_summary, 'status_code'):
                result = json_data['result']
                increment_key(result, status_summary, 'status')
                status = result['status']
                if status == 'ok':
                    increment_key(result, language_summary, 'language')
                    segments = result['segments']
                    for segment in segments:
                        increment_key(segment, segment_summary, 'name')
            pbar.update(1)

    for summary in (status_summary,
                    status_code_summary,
                    language_summary,
                    segment_summary):
        print_summary(summary, lines)


if __name__ == '__main__':
    infile = sys.argv[1]
    summarise(infile)
