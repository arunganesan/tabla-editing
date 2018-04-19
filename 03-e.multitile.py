#! /usr/bin/env python

"""
Take the trimmed files.
Take input a list of video files and the master audio file.
For each video file, we will simply tile them in a pleasing way.
Then glue on audio track.
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
    
    # Split files
    for idx, video_file in enumerate(all_video_files):
        basename, ext = os.path.splitext(video_file)
        filename = '{}/trimmed-{}'.format(args.processdir, video_file)
        
        command = "ffmpeg"
        command += " -i {} -an".format(filename)
        command += " -q:v 4"

        # This scales and crops
        command += ' -vf "scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}:(ow-iw)/2:(oh-ih)/2"'.format(width=WIDTH/2, height=HEIGHT/2)
        command += " {}/cropped-{}.ts".format(args.processdir, basename)
        os.system(command)
    
    # Mosaic
    # https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
    command = "ffmpeg"
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        filename = "{}/cropped-{}.ts".format(args.processdir, basename)
        command += " -i {} -an".format(filename)
    
    OFILE = 'mosaic.mp4'
    command += ' -filter_complex "'
    command += " nullsrc=size={}x{} [base];".format(WIDTH, HEIGHT)

    import math
    GRID = int(math.ceil(math.sqrt(len(all_video_files))))
    cell_width = WIDTH/GRID
    cell_height = HEIGHT/GRID

    for idx in range(len(all_video_files)):
        command += ' [{idx}:v] setpts=PTS-STARTPTS, scale={w}x{h} [video-{idx}];'.format(idx=idx, w=cell_width, h=cell_height)
    
    counter = 0
    for row in range(GRID):
        y = row * cell_height
        for col in range(GRID):
            x = col * cell_width
            
            if counter == 0:
                command += ' [base][video-{c}] overlay=shortest=1 [tmp{n}];'.format(c=counter, n=counter+1)
            elif counter == len(all_video_files) - 1:
                command += ' [tmp{c}][video-{c}] overlay=shortest=1:x={x}:y={y}'.format(c=counter, x=x, y=y)
            else:
                command += ' [tmp{c}][video-{c}] overlay=shortest=1:x={x}:y={y} [tmp{n}];'.format(c=counter, n=counter+1, x=x, y=y)
            
            counter += 1
            if counter == len(all_video_files): 
                break

        if counter == len(all_video_files):
            break

    #command += ' [0:v] setpts=PTS-STARTPTS, scale={}x{} [upperleft];'.format(WIDTH/2, HEIGHT/2)
    #command += ' [1:v] setpts=PTS-STARTPTS, scale={}x{} [upperright];'.format(WIDTH/2, HEIGHT/2)
    #command += ' [2:v] setpts=PTS-STARTPTS, scale={}x{} [lowerleft];'.format(WIDTH/2, HEIGHT/2)
    #command += ' [base][upperleft] overlay=shortest=1 [tmp1];'
    #command += ' [tmp1][upperright] overlay=shortest=1:x={} [tmp2]; '.format(WIDTH/2)
    #command += ' [tmp2][lowerleft] overlay=shortest=1:y={}'.format(HEIGHT/2)
    command += ' "'
    command += ' -c:v libx264 {}/{}'.format(args.processdir, OFILE)
    os.system(command)
    

    # Glue audio file
    command = 'ffmpeg -y -i {}/{}'.format(args.processdir, OFILE)
    command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
    command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' {}/glued-{}'.format(args.processdir, OFILE)
    os.system(command)
    
main()
