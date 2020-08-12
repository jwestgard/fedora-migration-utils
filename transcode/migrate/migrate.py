#!/usr/bin/env python3

import csv
#import ffmpy
import os
import shutil
import sys
from fedora import Umdm, Umam, DigitalAsset


def main():

    ecount = 0
    ccount = 0
    tcount = 0

    dest_root   = ""
    origin_root = ""
    efile       = "/Users/westgard/Desktop/error.txt"
    cfile       = "/Users/westgard/Desktop/copy.txt"
    tfile       = "/Users/westgard/Desktop/transcode.txt"

    # the set of all item-level objects
    itemset = set()

    # read the data file and create items and components
    with open(sys.argv[1]) as handle:

        for row in csv.DictReader(handle):
            # create the item or pull existing from registry
            umdm = Umdm.from_registry(
                pid = row['pid'], 
                collection = row['isMemberOfCollection']
                )
            # create the component object
            umam = Umam.from_registry(
                pid = row['hasPart'], 
                identifier = row['identifier']
                )
            # create the digital asset object
            if row['restore_filepath'].startswith("/libr/archives/projectsexport/"):
                relpath = row['restore_filepath'][30:]
            else:
                with open(efile, 'a+') as handle:
                    handle.write(row['pid'] + '\n')
                continue

            asset = DigitalAsset(
                row['restore_filename'], 
                bytes=int(row['restore_bytes']),
                md5=row['restore_md5'], 
                ext=row['file_extension'],
                path=relpath,
                )

            # add asset to the umam object
            umam.add_asset(asset)
            # add umam to the umdm object
            umdm.add_part(umam)
            # add the item to the dataset
            itemset.add(umdm)

    acount = sum([len(item.parts) for item in itemset])
    pcount = 0
    transcode = []

    for n, item in enumerate(sorted(itemset), 1):

        print(f"{pcount}/{acount} (ERR:{ecount:04} | CPY:{ccount:04} | TRC:{tcount:04})",
              end='\r')

        if not item.is_well_formed():
            ecount += len(item.parts)
            with open(efile, 'a+') as handle:
                handle.write(item.pid + '\n')

        else:
            for part in item.parts:
                if part.has_access_version():
                    ccount += 1
                    for asset in part.assets:
                        if asset.role == "access":
                            outdir = os.path.join(
                                dest_root, item.pathsafe_pid, part.pathsafe_pid
                                )
                            #os.makedirs(outdir, exist_ok=True)
                            outpath = os.path.join(outdir, asset.filename)
                            if not os.path.isfile(outpath):
                                inpath = os.path.join(origin_root, asset.path)
                                print()
                                print(f"Copying {inpath} to {outpath}")
                                #shutil.copy(inpath, outpath)

                elif part.has_master_version():
                    tcount += 1
                    for asset in part.assets:
                        if asset.role == "master":
                            inpath = os.path.join(origin_root, asset.path)
                            outdir = os.path.join(
                                dest_root, item.pathsafe_pid, part.pathsafe_pid
                                )
                            #os.makedirs(outdir, exist_ok=True)
                            if asset.ext == "mov":
                                new_ext = "mp4"
                            elif asset.ext =="wav":
                                new_ext = "mp3"
                            else:
                                new_ext = "unknown"
                            outpath = os.path.join(
                                outdir, asset.basename + "." + new_ext
                                )
                            transcode.append((inpath, outpath))
                            '''with open(tfile, 'a+') as handle:
                                cmd = f'ffmpeg -i "{inpath}" "{outpath}"'
                                handle.write(cmd + '\n')'''

                else:
                    print(f"An unknown error occurred with {part.pid}")
                    sys.exit()

        pcount += 1

    with open(tfile, 'w') as handle:
        writer = csv.writer(handle)
        for item in transcode:
            writer.writerow(item)

    print(f"items: {len(itemset)} | UMAM: {acount} | Copy: {ccount} | Convert: {tcount}")

if __name__ == "__main__":
    main()
