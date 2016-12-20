import os
import sys

def _line_count(infile):
    '''returns the number of lines in file `infile`
    '''
    # fastest pure python way I could find for big files, although calling "wc
    # -l" with subprocess.check_output is faster (but depends on wc being
    # present).

    size = 65536
    count = 0
    while True:
        b = infile.read(size)
        if not b:
            break
        count += b.count(os.linesep)
    return count


def line_count(infile):
    # don't try to count the lines on stdin
    if infile == sys.stdin:
        return 0
    pos = infile.tell()
    count = _line_count(infile)
    infile.seek(pos)
    return count
