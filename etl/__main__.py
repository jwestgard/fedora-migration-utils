#!/usr/bin/env python3

import argparse
import csv
import lxml
import os
import yaml

from .fcrepo import Foxml


def get_args():
    """Parse command line arguments and return namespace object"""
    parser = argparse.ArgumentParser(description='Extract FOXML data to CSV')
    parser.add_argument('-m', action="store", dest="mapping", required=True)
    parser.add_argument('-s', action="store", dest="source", required=True)
    parser.add_argument('-o', action="store", dest="output", required=True)
    return parser.parse_args()


def read_mapping(source):
    """Read the YAML mapping file and return a dictionary of keys and values"""
    with open(source) as sourcefile:
        mapping = yaml.safe_load(sourcefile)
    return mapping


def main():

    args = get_args()
    src_dir = args.source
    out_csv = args.output
    mapping = read_mapping(args.mapping)
    filecount = 0

    print(f"\n=======================")
    print(f"| FEDORA 2 ETL SCRIPT |")
    print(f"=======================")
    print(f" SOURCE DIR: {src_dir}")
    print(f"    MAPPING: {mapping}")
    print(f"   DEST CSV: {out_csv}\n")

    with open(out_csv, 'w') as outputfile:
        writer = csv.DictWriter(outputfile, fieldnames=mapping.keys())
        writer.writeheader()
        for current, subdirs, files in os.walk(src_dir):
            for file in files:
                filepath = os.path.join(current, file)
                filecount += 1
                print(f"({filecount}) {filepath}")

if __name__ == "__main__":
    main()