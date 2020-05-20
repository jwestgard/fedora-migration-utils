#!/usr/bin/env python3

from multiprocessing import Pool
import argparse
import csv
import logging
import os
import subprocess
import sys
import time


INPUTFILE   = sys.argv[1]
OUTPUTFILE  = sys.argv[2]

"""
OUTPUTROOT = sys.argv[3]
LOGDIR     = sys.argv[4]
"""

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
    with open(INPUTFILE) as infile, open(OUTPUTFILE, 'w') as outfile:
        fieldnames = ['umdm', 'umam', 'type', 'base', 'ext', 'status', 'source']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for source, destination in csv.reader(infile):
            umdm, umam, filename = destination.split('/')
            base, ext = os.path.splitext(filename)
            if ext == '.mp3':
                type = 'audio'
            elif ext == '.mp4':
                type = 'video'
            else:
                print(f'ERROR {base} {ext}')
                sys.exit()

            writer.writerow({
                'source': source,
                  'umdm': umdm,
                  'umam': umam,
                  'base': base,
                   'ext': ext,
                  'type': type,
                'status': 'todo'
                })

    """
    files = [tuple(row) for row in csv.reader(open(INPUTFILE))]
    p = Pool(2)
    p.starmap(transcode, files)
    """

if __name__ == "__main__":
    main()
