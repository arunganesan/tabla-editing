#! /usr/bin/env python
import os
import json
import argparse

WIDTH = 2100; #1920.0
HEIGHT = 1000#1080.0

parser = argparse.ArgumentParser()
parser.add_argument('processdir')
args = parser.parse_args()

DIR = args.processdir
assert os.path.exists('{}/manual'.format(DIR))
spec = json.loads(open('{}/manual'.format(DIR)).read())
FROM_TIME = spec['start']
DURATION = spec['duration']
TEXT = spec['text']
for idx in range(len(TEXT)):
    TEXT[idx][0] -= FROM_TIME
spec.setdefault('audioDelay', 0)
AUDIO_DELAY = spec['audioDelay']

# Crop into the manually chosen video
IFILE = '{}/glued-mosaic.mp4'.format(DIR)
OFILE = '{}/edited-final.mp4'.format(DIR)
command = 'ffmpeg -y -i {ifile} -itsoffset {} -i {ifile} -map 0:v -map 1:a -ss {} -t {} {}'.format(AUDIO_DELAY, FROM_TIME, DURATION, OFILE, ifile=IFILE)
os.system(command)

# Make black
command = 'convert -size {}x{} xc:black {}/black.png'.format(WIDTH/2, HEIGHT/2, DIR)
os.system(command)

# Make each text slide
FONT = 'Gentium-Basic-Regular'
for idx, (start, text) in enumerate(TEXT):
    command = 'convert -font {} -fill white -pointsize 60 -gravity center -draw "text 0,0 '.format(FONT)
    command += "'{}'".format(text)
    command += '" {}/black.png {}/{}.png'.format(DIR, DIR, idx)
    os.system(command)

# Add all text images to the video
command = 'ffmpeg -y -i {}'.format(OFILE)
for idx in range(len(TEXT)):
    command += ' -i {}/{}.png'.format(DIR, idx)

command += ' -filter_complex "'
last_filter_out = '[0:v]'
for idx, (start, text) in enumerate(TEXT):
    end = DURATION
    if idx < len(TEXT)-1:
        end = TEXT[idx+1][0]

    command += "{}[{}:v] overlay={}:{}:".format(last_filter_out, idx+1, WIDTH/2, HEIGHT/2)
    command += "enable='between(t,{},{})'".format(start, end)
    last_filter_out = '[l{}]'.format(idx)
    if idx < len(TEXT)-1:
        command += last_filter_out + ';'
command += '" -pix_fmt yuv420p -c:a copy {}/with-caption.mp4'.format(DIR)
os.system(command)

# Compress for Instagram
command = 'ffmpeg -y -i {}/with-caption.mp4'.format(DIR)
command += ' -vcodec mpeg4 -vb 8000k -strict experimental -qscale 0 {}/with-caption-compressed.mp4'.format(DIR)
os.system(command)
