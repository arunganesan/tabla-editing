#! /usr/bin/env python

"""
Using the chirp file, we will trim all video files and the master audio file.
Then, we will crop the video file into parts and glue them together
Finally, strip the audio channel of the glued together file and replace with the master audio track
"""

OFILE = 'chirps'
WIDTH = 2100# 1920
HEIGHT = 1000 #1080

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
    import os, json


    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()
    
    specfile = '{}/spec'.format(args.processdir)
    assert os.path.exists(specfile)
    lines = open(specfile).readlines()
    assert len(lines) >= 2
    master_audio_file = lines[0].strip()
    all_video_files = [l.strip() for l in lines[1:]]
    
    chirpfile = '{}/chirps'.format(args.processdir)
    assert os.path.exists(chirpfile)
    chirp_data = json.loads(open(chirpfile).read())
  
    # Split files
    for idx, video_file in enumerate(all_video_files):
        basename, ext = os.path.splitext(video_file)
        filename = '{}/trimmed-{}'.format(args.processdir, video_file)
        
        command = "ffmpeg -y"
        command += " -i {} -an".format(filename)
        command += " -q:v 4"

        # This scales and pads
        #command += ' -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"'
        
        # This scales and crops
        command += ' -vf "scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}:(ow-iw)/2:(oh-ih)/2"'.format(width=WIDTH/2, height=HEIGHT/2)
        command += " {}/cropped-{}.ts".format(args.processdir, basename)
        os.system(command)
    
    # Mosaic
    # https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
    command = "ffmpeg -y"
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        filename = "{}/cropped-{}.ts".format(args.processdir, basename)
        command += " -i {} -an".format(filename)
    
    OFILE = 'mosaic.mp4'
    command += ' -filter_complex "'
    command += " nullsrc=size={}x{} [base];".format(WIDTH, HEIGHT)
    command += ' [0:v] setpts=PTS-STARTPTS, scale={}x{} [upperleft];'.format(WIDTH/2, HEIGHT/2)
    command += ' [1:v] setpts=PTS-STARTPTS, scale={}x{} [upperright];'.format(WIDTH/2, HEIGHT/2)
    command += ' [2:v] setpts=PTS-STARTPTS, scale={}x{} [lowerleft];'.format(WIDTH/2, HEIGHT/2)
    command += ' [base][upperleft] overlay=shortest=1 [tmp1];'
    command += ' [tmp1][upperright] overlay=shortest=1:x={} [tmp2]; '.format(WIDTH/2)
    command += ' [tmp2][lowerleft] overlay=shortest=1:y={}'.format(HEIGHT/2)
    command += ' "'
    command += ' -c:v libx264 {}/{}'.format(args.processdir, OFILE)
    os.system(command)
    
    command = 'ffmpeg -y -i {}/{}'.format(args.processdir, OFILE)
    command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
    command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' {}/glued-{}'.format(args.processdir, OFILE)
    os.system(command)
    
main()
