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
    import os


    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()
    
    import os
    specfile = '{}/spec'.format(args.processdir)
    assert os.path.exists(specfile)
    lines = open(specfile).readlines()
    assert len(lines) >= 2
    master_audio_file = lines[0].strip()
    all_video_files = [l.strip() for l in lines[1:]]
    
    chirpfile = '{}/chirps'.format(args.processdir)
    assert os.path.exists(chirpfile)
    chirp_lines = open(chirpfile).readlines()
    chirp_data = {}
    for line in chirp_lines:
        parts = line.split(' ')
        video_file = parts[0]
        start_at = float(parts[1])
        end_at = float(parts[2])
        chirp_data[video_file] = [start_at, end_at]
  
    # Split files
    length = chirp_data[master_audio_file][1] - chirp_data[master_audio_file][0]
    per_segment = length / float(len(all_video_files))

    for idx, video_file in enumerate(all_video_files):
        basename, ext = os.path.splitext(video_file)
        filename = '{}/trimmed-{}'.format(args.processdir, video_file)
        
        command = "ffmpeg -y "
        command += " -i {} -an".format(filename)
        command += " -q:v 4"
        command += ' -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"'
        command += " {}/cropped-{}.ts".format(args.processdir, basename)
        os.system(command)
    
        """
        ffmpeg
        -i 1.avi -i 2.avi -i 3.avi -i 4.avi
        -filter_complex "
                nullsrc=size=640x480 [base];
                [0:v] setpts=PTS-STARTPTS, scale=320x240 [upperleft];
                [1:v] setpts=PTS-STARTPTS, scale=320x240 [upperright];
                [2:v] setpts=PTS-STARTPTS, scale=320x240 [lowerleft];
                [3:v] setpts=PTS-STARTPTS, scale=320x240 [lowerright];
                [base][upperleft] overlay=shortest=1 [tmp1];
                [tmp1][upperright] overlay=shortest=1:x=320 [tmp2];
                [tmp2][lowerleft] overlay=shortest=1:y=240 [tmp3];
                [tmp3][lowerright] overlay=shortest=1:x=320:y=240
        "
        -c:v libx264 output.mkv" 
        """    
    # Mosaic
    # https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
    command = "ffmpeg -y"
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        filename = "{}/cropped-{}.ts".format(args.processdir, basename)
        command += " -i {} -an".format(filename)
    
    OFILE = 'mosaic.mp4'
    command += ' -filter_complex "'
    command += " nullsrc=size=1920x1080 [base];"
    command += ' [0:v] setpts=PTS-STARTPTS, scale=960x540 [upperleft];'
    command += ' [1:v] setpts=PTS-STARTPTS, scale=960x540 [upperright];'
    command += ' [2:v] setpts=PTS-STARTPTS, scale=960x540 [lowerleft];'
    command += ' [base][upperleft] overlay=shortest=1 [tmp1];'
    command += ' [tmp1][upperright] overlay=shortest=1:x=960 [tmp2]; '
    command += ' [tmp2][lowerleft] overlay=shortest=1:y=540'
    command += ' "'
    command += ' -c:v libx264 {}/{}'.format(args.processdir, OFILE)
    os.system(command)
    
    command = 'avconv -y -i {}/{}'.format(args.processdir, OFILE)
    command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
    command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' {}/glued-{}'.format(args.processdir, OFILE)
    os.system(command)
    
main()
