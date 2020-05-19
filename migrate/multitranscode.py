#!/usr/bin/env python3

from multiprocessing import Pool
import csv
import os
import subprocess
import sys
import time


INPUTFILE  = sys.argv[1]
INPUTROOT  = sys.argv[2]
OUTPUTROOT = sys.argv[3]
LOGDIR     = sys.argv[4]


def transcode(source, destination):
    filename  = os.path.basename(source)
    base, ext = os.path.splitext(filename)
    inpath    = os.path.join(INPUTROOT, source)
    outpath   = os.path.join(OUTPUTROOT, destination)
    logpath   = os.path.join(LOGDIR, base, str(int(time.time())) + '.log')   

    if filename.endswith('mov'):
        cmd = f"ffmpeg -n -i {inpath} -vcodec h264 -acodec mp2 {outpath}"
    elif filename.endswith('wav'):
        cmd = f"ffmpeg -n -i {inpath} -acodec libmp3lame {outpath}"
    else:
        cmd = None

    os.makedirs(os.path.dirname(logpath), exist_ok=True)
    with open(logpath, 'w') as handle:
        output = subprocess.run(cmd, stderr=handle, text=True, shell=True)


def main():
    files = [tuple(row) for row in csv.reader(open(INPUTFILE))]
    p = Pool(2)
    p.starmap(transcode, files)


if __name__ == "__main__":
    main()
