#!/usr/bin/env zsh

PID=${1//[^a-zA-Z0-9]/}
SOURCE=$2
FILENAME=$(basename $SOURCE)
OUTPUT=$PID/$FILENAME

mkdir -p $PID
ffmpeg -i "/Volumes/LIBRDCRProjectsShare/$SOURCE" -vcodec h264 -acodec mp4 "$OUTPUT"