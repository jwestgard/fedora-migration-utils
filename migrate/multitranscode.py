#!/usr/bin/env python3

from multiprocessing import Pool
from multiprocessing import Process
import os
import sys


def run_ffmpeg():
    pass


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def f(name):
    info('function f')
    print('hello', name)


def main():
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()


if __name__ == "__main__":
    main()
