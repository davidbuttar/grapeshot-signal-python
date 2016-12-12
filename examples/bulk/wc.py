import subprocess
import sys
import timeit
import os


# Quick test on a file with ~ 1.4 million lines:
# python wc.py lines.txt
# 14279660
# 0.40809741197153926
# 14279660
# 2.318539552972652
# 14279660
# 2.4829419250017963
# 14279660
# 1.3983664290281013


def wc_subprocess(fname):
    output = subprocess.check_output(["wc", "-l", fname])
    return int(output.split(b' ')[0])


def wc_enumerate_lines(fname):
    with open(fname) as f:
        for i, _ in enumerate(f):
            pass
        return i+1


def wc_iterate_lines(fname):
    with open(fname) as f:
        return sum(1 for _ in f)


def wc_blocks(fname):
    size = 65536
    count = 0
    with open(fname) as f:
        while True:
            b = f.read(size)
            if not b:
                break
            count += b.count(os.linesep)
    return count


def time_wc(funcname, filename):
    setup = 'from __main__ import {}'.format(funcname)
    stmt = '{}("{}")'.format(funcname, filename)
    return timeit.timeit(stmt, setup=setup, number=1)

if __name__ == '__main__':
    fname = sys.argv[1]

    print(wc_subprocess(fname))
    print(time_wc('wc_subprocess', fname))

    print(wc_enumerate_lines(fname))
    print(time_wc('wc_enumerate_lines', fname))

    print(wc_iterate_lines(fname))
    print(time_wc('wc_iterate_lines', fname))

    print(wc_blocks(fname))
    print(time_wc('wc_blocks', fname))
