#!/usr/bin/env python3

from multiprocessing import Pool
import argparse
import csv
import logging
import os
import subprocess
import sys
import time
import yaml


def get_args():
    """Parse command line arguments and return namespace object"""
    parser = argparse.ArgumentParser(description='Transcode some files')
    parser.add_argument('-c', action="store", dest="config", required=True)
    parser.add_argument('-l', action="store", dest="limit", type=int, default=None)
    parser.add_argument('-p', action="store", dest="processes", type=int)
    parser.add_argument('-q', action="store_true", dest="quiet")
    return parser.parse_args()


def transcode(**kwargs):
    """Process a single file with the appropriate ffmpeg command and return results"""
    inpath  = os.path.join(kwargs['sourcedir'], kwargs['source'])
    relpath = os.path.join(kwargs['umdm'], kwargs['umam'])
    outpath = os.path.join(kwargs['destdir'], relpath, kwargs['base'] + kwargs['ext'])
    ffmpeg  = kwargs['ffmpeg']
    logfile = str(int(time.time())) + '.log'
    logpath = os.path.join(kwargs['logdir'], relpath, kwargs['base'], logfile)
    logging.info(f"Source file: {inpath}")
    logging.info(f"Destination: {outpath}")
    logging.info(f"Results log: {logpath}")

    if kwargs['type'] == "video":
        cmd = (f'{ffmpeg} -y -nostdin -i "{inpath}" -vcodec h264 -acodec mp2 "{outpath}"')
    elif kwargs['type'] == "audio":
        cmd = (f'{ffmpeg} -y -nostdin -i "{inpath}" -acodec libmp3lame "{outpath}"')

    os.makedirs(os.path.dirname(logpath), exist_ok=True)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    logging.info(f"Calling cmd: '{cmd}'")
    with open(logpath, 'w') as handle:
        return subprocess.run(cmd, stderr=handle, text=True, shell=True)


def main():

    # Parse command-line arguments
    args = get_args()

    # Set up logger
    logging.basicConfig(format='%(asctime)s - %(message)s', 
                        level=logging.WARNING if args.quiet else logging.INFO
                        )

    with open(args.config) as configfile:
        config = (yaml.safe_load(configfile))
        ffmpeg    = config['ffmpeg']
        manifest  = config['manifest']
        job_log   = config['job_log']
        sourcedir = config['sourcedir']
        destdir   = config['destdir']
        logdir    = config['logdir']

    logging.warning('================================')
    logging.warning('*** FFMPEG TRANSCODING QUEUE ***')
    logging.warning('================================')
    logging.info(f'Running with these command-line args:')
    for k, v in args.__dict__.items():
        logging.info(f'  {k: <10}: {v}')

    logging.info(f'Running with these configuration settings:')
    for k, v in config.items():
        logging.info(f'  {k: <10}: {v}')
    proc_count = 0
    skip_count = 0

    # Load manifest
    with open(config['manifest']) as infile:
        queue = [row for row in csv.DictReader(infile)]
        logging.warning(f'Loaded {len(queue)} items from {manifest}')

    # Read existing job log for completed items
    if os.path.isfile(job_log):
        logging.info(f'Reading completed jobs from {job_log}')
        complete = {}
        with open(job_log, 'r') as handle:
            for row in csv.DictReader(handle):
                key = row['source']
                complete[key] = row
        logging.info(f'Found {len(complete)} complete items')
    else:
        complete = {}

    # Process each item
    if args.limit:
        logging.warning(f'Processingcat {args.limit} items')
    else:
        logging.warning(f'Processing {len(queue)} items')
    with open(job_log, 'w+') as outfile:
        fieldnames = ['umdm', 'umam', 'type', 'base', 'ext', 'status', 'source']
        logging.info(f'Opening {job_log} to record results')
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for n, item in enumerate(queue, 1):
            try:
                # If the processing limit has been reached
                key = item['source']
                if args.limit and proc_count >= args.limit:
                    logging.info(f'Writing remaining completed items to results')
                    for item_record in complete.values():
                        writer.writerow(item_record)
                    break
                # If the source is found among the completed items
                elif key in complete and complete[key].get('status') == 'done':
                    item_record = complete.get(key)
                    skip_count += 1
                    logging.info(f"({n}) Skipping {item_record['base']}")
                    writer.writerow(item_record)
                # If the item has not been processed
                else:
                    proc_count += 1
                    logging.info(f"({n}) Processing {item['base']}")
                    results = transcode(**item, 
                                        sourcedir=sourcedir, 
                                        destdir=destdir,
                                        logdir=logdir,
                                        ffmpeg=ffmpeg
                                        )
                    # Evaluate the results of transcoding
                    if results.returncode == 0:
                        logging.info(f'  => Success')
                        item['status'] = 'done'
                    else:
                        logging.info(f'  => Failed')
                        item['status'] = 'failed'
                    writer.writerow(item)
            # Handle unexpected errors by stopping processing
            except Exception as e:
                logging.info(f'Something unexpected happened.')
                print(e)
                sys.exit()

    # Report program results
    logging.warning(f"+===== RESULTS REPORT =====+")
    logging.warning(f"|   PROCESSED {proc_count:04} ITEMS   |")
    logging.warning(f"|     SKIPPED {skip_count:04} ITEMS   |")
    logging.warning(f"+==========================+")
    logging.warning(f"*** PROGRAM END, GOODBYE ***")



if __name__ == "__main__":
    main()
