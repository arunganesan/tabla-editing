#! /usr/bin/env python


import os


DIR = 'recordings/04.05.2018'
FROM_TIME = 71
DURATION = 60
TEXT = [
    [0, 3, '3/6/12 bhajan beats'],
    [3, 14, 'Dha Na Tet, Na Dha Tet'],
    [14, 24, 'Dha Dhin Na, Ta Dhin Na'],
    [24, 35, 'Dha Ge Tin, Na Tin -\nNa Ge Tin, Na Tin -'],
    [35, 60, 'Ektal\nDhin, Dhin, Dhage \nTRKT, TuNa, KatTa\nDhage, TRKT, Dhin, Nana']
]



IFILE = '{}/glued-mosaic.mp4'.format(DIR)
OFILE = '{}/edited-final.mp4'.format(DIR)
command = 'ffmpeg -y -i {} -ss {} -t {} {}'.format(IFILE, FROM_TIME, DURATION, OFILE)
os.system(command)


# Make black

command = 'convert -size 960x540 xc:black {}/black.png'.format(DIR)
os.system(command)

for idx, (start, end, text) in enumerate(TEXT):
    # Make image

    command = 'convert -font helvetica -fill white -pointsize 60 -gravity center -draw "text 0,0 '
    command += "'{}'".format(text)
    command += '" {}/black.png {}/{}.png'.format(DIR, DIR, idx)
    os.system(command)

command = 'ffmpeg -y -i {}'.format(OFILE)
for idx in range(len(TEXT)):
    command += ' -i {}/{}.png'.format(DIR, idx)

command += ' -filter_complex "'
last_filter_out = '[0:v]'
for idx, (start, end, text) in enumerate(TEXT):
    command += "{}[{}:v] overlay=960:540:".format(last_filter_out, idx+1)
    command += "enable='between(t,{},{})'".format(start, end)
    last_filter_out = '[l{}]'.format(idx)
    if idx < len(TEXT)-1:
        command += last_filter_out + ';'
command += '" -pix_fmt yuv420p -c:a copy {}/with-caption.mp4'.format(DIR)
os.system(command)
