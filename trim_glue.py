#! /usr/bin/env python

"""
Using the chirp file, we will trim all video files and the master audio file.
Then, we will crop the video file into parts and glue them together
Finally, strip the audio channel of the glued together file and replace with the master audio track
"""

OFILE = 'chirps'

import numpy as np

def read_and_normalize_audio (audiofile):
  from scipy.io import wavfile
  rate, signal = wavfile.read(audiofile)
  converted = np.array(signal, dtype=np.float64)
  normalized = converted / np.amax(converted)
  return rate, normalized 


def main():
    import argparse
    import numpy as np
    import scipy.signal as sps
    from tqdm import tqdm
    from glob import glob
    import json
    import os


    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()
    
    master_audio_file = 'master.wav'
    all_video_files = glob('{}/*.mov'.format(args.processdir))
    all_video_files += glob('{}/*.MOV'.format(args.processdir))
    all_video_files = [os.path.basename(f) for f in all_video_files]
    
    chirpfile = '{}/chirps'.format(args.processdir)
    assert os.path.exists(chirpfile)
    chirp_data = json.loads(open(chirpfile).read())
    
    # Trim files
    import subprocess
    # Master audio file
    start_at = chirp_data[master_audio_file]
    command = 'ffmpeg -ss {}'.format(start_at)
    command += ' -i {homedir}/{master} {homedir}/trimmed-{master}'.format(homedir=args.processdir, master=master_audio_file)
    os.system(command)
    
    for video_file in all_video_files:
        start_at = chirp_data[video_file]
        basename, ext = os.path.splitext(video_file)
        filename = '{}/{}'.format(args.processdir, video_file)
        command = 'ffmpeg -i {}'.format(filename)
        command += ' -ss {}'.format(start_at)
        command += ' -an' # Ignore audio track
        command += ' -r 25' # re-encode 
        command += ' {}/trimmed-{}{}'.format(args.processdir, basename, ext)
        #command += ' -c copy {}/trimmed-{}{}'.format(args.processdir, basename, ext)
        os.system(command)
    
    
    # Add in our new sound track
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        command = 'ffmpeg -i {}/trimmed-{}'.format(args.processdir, video_file)
        command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
        command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
        command += ' {}/glued-{}'.format(args.processdir, video_file)
        os.system(command)
        #avconv -i stripped-dslr.mov -i trimmed-mictrack.wav -shortest -c:v copy -c:a mp3 -b:a 256k glued-dslr.mov

main()
