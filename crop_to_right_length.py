#! /usr/bin/env python
import os
import json
import argparse
from readgrid import read_spec


parser = argparse.ArgumentParser()
parser.add_argument('processdir')
args = parser.parse_args()
DIR = args.processdir


assert os.path.exists('{}/caption.json'.format(DIR))
spec = json.loads(open('{}/caption.json'.format(DIR)).read())
FROM_TIME = spec['start']
DURATION = spec['duration']
TEXT = spec['text']
for idx in range(len(TEXT)):
    TEXT[idx][0] -= FROM_TIME



from glob import glob
trimmed_files = glob('{}/trimmed-*mov'.format(DIR))
trimmed_files += glob('{}/trimmed-*MOV'.format(DIR))
for f in trimmed_files:
    savename = f.replace('trimmed-', 'cropped-')
    command = 'ffmpeg -y -i {} -ss {} -t {} {}'.format(f, FROM_TIME, DURATION, savename)
    print command
    os.system(command)

command = 'ffmpeg -y -i {}/trimmed-master.wav -ss {} -t {} {}/cropped-master.wav'.format(DIR, FROM_TIME, DURATION, DIR)
print command
os.system(command)


