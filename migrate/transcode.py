#!/usr/bin/env python3

from multiprocessing import Pool
import argparse
import csv
import logging
import os
import subprocess
import sys
import time


#MANIFEST = sys.argv[1]
SRCDIR   = "/libr/archives/projectsexport"
DSTDIR   = "/libr/avalonmigration/data"
LOGDIR   = "/libr/avalonmigration/logs"


def get_args():
    parser = argparse.ArgumentParser(description='Transcode some files')
    parser.add_argument('-m', action="store", dest="manifest")
    parser.add_argument('-l', action="store", dest="limit", type=int)
    parser.add_argument('-p', action="store", dest="processes", type=int)
    parser.add_argument('-q', action="store_true", dest="quiet")
    return parser.parse_args()


def transcode(**kwargs):
    inpath  = os.path.join(SRCDIR, kwargs['source'])
    relpath = os.path.join(kwargs['umdm'], kwargs['umam'])
    outpath = os.path.join(DSTDIR, relpath, kwargs['base'] + kwargs['ext'])
    logfile = str(int(time.time())) + '.log'
    logpath = os.path.join(LOGDIR, relpath, kwargs['base'], logfile)

    if kwargs['type'] == "video":
        cmd = f'/libr/avalonmigration/bin/ffmpeg -y -nostdin -i "{inpath}" -vcodec h264 -acodec mp2 "{outpath}"'
    elif kwargs['type'] == "audio":
        cmd = f'/libr/avalonmigration/bin/ffmpeg -y -nostdin -i "{inpath}" -acodec libmp3lame "{outpath}"'

    os.makedirs(os.path.dirname(logpath), exist_ok=True)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    with open(logpath, 'w') as handle:
        return subprocess.run(cmd, stderr=handle, text=True, shell=True)


def main():

    # Parse command-line arguments
    args = get_args()
    
    # Set up logger
    logging.basicConfig(format='%(asctime)s - %(message)s', 
                        level=logging.WARNING if args.quiet else logging.INFO
                        )
    logging.warning('*** FFMPEG TRANSCODING QUEUE ***')
    fieldnames = ['umdm', 'umam', 'type', 'base', 'ext', 'status', 'source']
    proc_count = 0
    skip_count = 0

    # Load manifest
    with open(args.manifest) as infile:
        queue = [row for row in csv.DictReader(infile)]
        logging.warning(f'Loaded {len(queue)} items from {args.manifest}')

    # Make a copy of the original manifest
    os.rename(args.manifest, args.manifest + '.bak')
    
    # Process each item
    with open(args.manifest, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        logging.info(f'Reopening {args.manifest} to record results')
        for n, item in enumerate(queue, 1):
            try:
                if item['status'] == 'done' or proc_count >= args.limit:
                    skip_count += 1
                    logging.info(f"({n}) Skipping {item['base']}")
                else:
                    proc_count += 1
                    logging.info(f"({n}) Processing {item['base']}")
                    results = transcode(**item)
                    if results.returncode == 0:
                        logging.info(f'   -> Success')
                        item['status'] = 'done'
                    else:
                        logging.info(f'   -> Failed')
                        item['status'] = 'failed'
                    writer.writerow(item)
            except:
                logging.info(f'Something unexpected happened.')
                sys.exit()

    # Report program results
    logging.warning(f"+=== RESULTS REPORT ===+")
    logging.warning(f"| PROCESSED {proc_count:04} ITEMS |")
    logging.warning(f"|   SKIPPED {skip_count:04} ITEMS |")
    logging.warning(f"+======================+") 
    logging.warning(f"*** PROGRAM END, GOODBYE ***")


if __name__ == "__main__":
    main()
