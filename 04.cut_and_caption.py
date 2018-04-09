#! /usr/bin/env python


import os



"""
DIR = 'recordings/04.05.2018'
FROM_TIME = 71
DURATION = 60
TEXT = [
    [0, 3, '3/6/12 bhajan beats'],
    [3, 14, 'Dha Na Tet, Na Dha Tet'],
    [14, 24, 'Dha Dhin Na, Ta Dhin Na'],
    [24, 35, 'Dha Ge Tin, Na Tin -\nNa Ge Tin, Na Tin -'],
    [35, 60, 'Ektal\n\nDhin, Dhin, Dhage \nTRKT, Tu, Na, Kat, Ta\nDhage, TRKT, Dhin, Nana']
]
"""

"""
DIR = 'recordings/04.06.2018'
FROM_TIME = 127
DURATION = 60
TEXT = [
    [0, 2, '4-beat bhajans'],
    [2, 15, 'Bhajani\n\nDhin -, Na Dhin, - Dhin, Na -\nTin -, Na Tin, - Tin, Na -'],
    [15, 22, 'Dhin -, Na Dhin, - Dhin, Na -\nTin -, Na Tin, - Tin, Na Na Kat Tet'],
    [22, 30, '... TRKT'],
    [30, 43, 'Dhe Ne, Na Na, - Te, Dha Na'],
    [43, 48, 'Keherewa\n\nDha Ge, Na Tu, Na Ge, Dhi Na'],
    [48, 54, 'Keherewa\nVariation 1\n\nDha Ge, Na Ka, Na Ka, Dhi -'],
    [54, 60, 'Keherewa\nVariation 2\n\nDha Ge, - Ka, Na Ka, Dhi -']
]
"""
"""
DIR = 'recordings/04.07.2018'
FROM_TIME = 20
DURATION = 38
TEXT = [
    [0, 11, 'Dha -, Dha -, Dha -, \nKTTK, Dhi -, KTTK, TRKT, TKTa-, \nTTKT, Ga Dhi Ge Ne, Ghin -, \nTe  Ran - -, -  Ne Dha -,\n Dhin -, Ta -, Kat - -\n(Dha -, Dhin -, Ta -, Kat - -)x2'],
    [11, 19, 'Repeat, faster'],
    [19, 27.5, 'Dha -, Dha -, Dha -, \nKTTK, Dhi -\nKTTK, TRKT, TKTa-, \nTTKT, Ga Dhi Ge Ne, Ghin -, \nTe  Ran - -, -  Ne Dha -, \n Dhin -, Ta -, Kat - -'],
    [27.5, 38, 'TRKT, TKTa-, TTKT, Ga Dhi Ge Ne,\nDha - KT, Dha - KT, Dha - - - (3x)']
]"""


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('processdir')
args = parser.parse_args()

DIR = args.processdir
import json, os

assert os.path.exists('{}/manual'.format(DIR))
spec = json.loads(open('{}/manual'.format(DIR)).read())
FROM_TIME = spec['start']
DURATION = spec['duration']
TEXT = spec['text']
for idx in range(len(TEXT)):
    TEXT[idx][0] -= FROM_TIME
AUDIO_DELAY = spec['audioDelay']

# Crop into the manually chosen video
IFILE = '{}/glued-mosaic.mp4'.format(DIR)
OFILE = '{}/edited-final.mp4'.format(DIR)
#ffmpeg.exe -i "movie.mp4" -itsoffset 3.84 -i "movie.mp4" -map 0:v -map 1:a -c copy "movie-audio-delayed.mp4"
command = 'ffmpeg -y -i {ifile} -itsoffset {} -i {ifile} -map 0:v -map 1:a -ss {} -t {} {}'.format(AUDIO_DELAY, FROM_TIME, DURATION, OFILE, ifile=IFILE)
os.system(command)


# Make black
command = 'convert -size 960x540 xc:black {}/black.png'.format(DIR)
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

    command += "{}[{}:v] overlay=960:540:".format(last_filter_out, idx+1)
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
