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

    # Trim files
    import subprocess
    # Master audio file
    [start_at, end_at] = chirp_data[master_audio_file]
    length = end_at - start_at
    command = 'avconv -ss {} -t {}'.format(start_at, length)
    command += ' -i {homedir}/{master} {homedir}/trimmed-{master}'.format(homedir=args.processdir, master=master_audio_file)
    os.system(command)
    
    for video_file in all_video_files:
        [start_at, end_at] = chirp_data[video_file]
        basename, ext = os.path.splitext(video_file)
        filename = '{}/{}'.format(args.processdir, video_file)
        length = end_at - start_at
        command = 'ffmpeg -i {}'.format(filename)
        command += ' -ss {} -to {}'.format(start_at, length)
        command += ' -an' # Ignore audio track
        command += ' -c copy {}/trimmed-{}{}'.format(args.processdir, basename, ext)
        os.system(command)
    
    
    # Add in our new sound track
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        command = 'avconv -i {}/trimmed-{}'.format(args.processdir, video_file)
        command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
        command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
        command += ' {}/glued-{}'.format(args.processdir, video_file)
        os.system(command)
        #avconv -i stripped-dslr.mov -i trimmed-mictrack.wav -shortest -c:v copy -c:a mp3 -b:a 256k glued-dslr.mov


    # This is for the concatenation trick
    # Divide into parts
    #length = chirp_data[master_audio_file][1] - chirp_data[master_audio_file][0]
    #per_segment = length / float(len(all_video_files))
    #for idx in range(len(all_video_files)):
    #    command = "avconv -ss {} -t {}".format(idx*per_segment, per_segment)
    #    command += " -i {homedir}/trimmed-{basename}.ts {homedir}/cropped-{basename}.ts".format(homedir=args.processdir, basename=all_video_files[idx])
    #    print command
    #    os.system(command)
    #
    ## Concat them together
    #command = 'avconv -i concat:"'
    #command += '|'.join(['{}/cropped-{}.ts'.format(args.processdir, basename) for basename in all_video_files])
    #command += '" -c copy -bsf:a aac_adtstoasc -y final.mp4'
    #os.system(command) 
    
main()
