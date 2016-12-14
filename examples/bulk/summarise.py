#!/usr/bin/env python3
import argparse
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


def output_summary(summary, outfile):
    with outfile as f:
        json.dump(summary, f)


def summarise(infile, outfile):
    lines = line_count(infile)
    pbar = tqdm.tqdm(total=lines)
    language_summary = collections.defaultdict(int)
    segment_summary = collections.defaultdict(int)
    status_code_summary = collections.defaultdict(int)
    status_summary = collections.defaultdict(int)
    with infile as f:
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

    result = {
        "status_summary": status_summary,
        "status_code_summary": status_code_summary,
        "language_summary": language_summary,
        "segment_summary": segment_summary
        }

    output_summary(result, outfile)


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
