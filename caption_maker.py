#! /usr/bin/env python
import os
import json
import argparse
from readgrid import read_spec


parser = argparse.ArgumentParser()
parser.add_argument('processdir')
args = parser.parse_args()
DIR = args.processdir

WIDTH = 1000; #1920.0
HEIGHT = 1000##1080.0


if os.path.exists('{}/gridspec.json'.format(DIR)):
    grid = read_spec('{}/gridspec.json'.format(DIR))
    if 'caption.mp4' in grid:
        spec = grid['caption.mp4']
        WIDTH = spec['width']
        HEIGHT = spec['height']

if WIDTH % 2 != 0: WIDTH += 1
if HEIGHT % 2 != 0: HEIGHT += 1


assert os.path.exists('{}/caption.json'.format(DIR))
spec = json.loads(open('{}/caption.json'.format(DIR)).read())
FROM_TIME = spec['start']
DURATION = spec['duration']
TEXT = spec['text']
for idx in range(len(TEXT)):
    TEXT[idx][0] -= FROM_TIME




# Make blank video of duration 
BLANK_FILE = '{}/empty.mp4'.format(DIR)
command = "ffmpeg -y -t {duration} -s {w}x{h} -f rawvideo -pix_fmt rgb24 -r 25 -i /dev/zero {ofile}".format(duration=DURATION, w=WIDTH, h=HEIGHT, ofile=BLANK_FILE)
os.system(command)

# Make black
command = 'convert -size {}x{} xc:black {}/black.png'.format(WIDTH, HEIGHT, DIR)
os.system(command)

# Make each text slide
FONT = 'Gentium-Basic-Regular'
for idx, (start, text) in enumerate(TEXT):
    command = 'convert -font {} -fill white -pointsize 50 -gravity center -draw "text 0,0 '.format(FONT)
    command += "'{}'".format(text)
    command += '" {}/black.png {}/{}.png'.format(DIR, DIR, idx)
    os.system(command)

# Add all text images to the video
command = 'ffmpeg -y -i {}'.format(BLANK_FILE)
for idx in range(len(TEXT)):
    command += ' -i {}/{}.png'.format(DIR, idx)

command += ' -filter_complex "'
last_filter_out = '[0:v]'
for idx, (start, text) in enumerate(TEXT):
    end = DURATION
    if idx < len(TEXT)-1:
        end = TEXT[idx+1][0]

    command += "{}[{}:v] overlay=0:0:".format(last_filter_out, idx+1)
    command += "enable='between(t,{},{})'".format(start, end)
    last_filter_out = '[l{}]'.format(idx)
    if idx < len(TEXT)-1:
        command += last_filter_out + ';'
command += '" -pix_fmt yuv420p -c:a copy {}/caption.mp4'.format(DIR)
print command
os.system(command)
