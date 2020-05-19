#!/usr/bin/env python3

import csv
import sys

inputfile = sys.argv[1]
audiofile = 'audio.sh'
videofile = 'video.sh'

with open(audiofile, 'w') as ahandle, open(videofile, 'w') as vhandle:
    for source, destination in csv.reader(open(inputfile)):
        if source.endswith('mov'):
            vhandle.write(f'ffmpeg -n -i "/libr/archives/projectsexport/{source}" ' +\
                                f'-vcodec h264 -acodec mp2 ' +\
                                f'"/libr/avalonmigration/{destination}"\n'
                                )
        elif source.endswith('wav'):
            ahandle.write(f'ffmpeg -n -i "/libr/archives/projectsexport/{source}" ' +\
                                f'-acodec libmp3lame ' +\
                                f'"/libr/avalonmigration/{destination}"\n'
                                )
        else:
            print("ERROR:", source, destination)
