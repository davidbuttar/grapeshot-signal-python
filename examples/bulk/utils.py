import os


def line_count(fname):
    '''returns the number of lines in file with name `fname`
    '''
    # fastest pure python way I could find for big files, although calling "wc
    # -l" with subprocess.check_output is faster (but depends on wc being
    # present).

    size = 65536
    count = 0
    with open(fname) as f:
        while True:
            b = f.read(size)
            if not b:
                break
            count += b.count(os.linesep)
    return count
