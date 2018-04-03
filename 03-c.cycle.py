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
    cycle_X_times = 10
    per_segment = length / cycle_X_times
    all_ofiles = []

    for idx in range(cycle_X_times):
        video_file = all_video_files[idx % len(all_video_files)]
        [start_at, end_at] = chirp_data[video_file]
        basename, ext = os.path.splitext(video_file)
        filename = '{}/trimmed-{}'.format(args.processdir, video_file)
        ofile = '{}/{}-{}.ts'.format(args.processdir, idx, basename)
        all_ofiles.append(ofile)
        
        command = "ffmpeg -y -ss {} -t {}".format(idx*per_segment, per_segment)
        command += " -i {} -an".format(filename)
        command += " -q:v 4"
        command += ' -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"'
        command += " {}".format(ofile)
        os.system(command)
    
    # Concat them together
    FINAL_FILE = 'cycle-final.mp4'
    command = 'avconv -i concat:"'
    command += '|'.join(all_ofiles)
    command += '" -c copy -bsf:a aac_adtstoasc -y {}/{}'.format(args.processdir, FINAL_FILE)
    os.system(command) 
    
    command = 'avconv -y -i {}/{}'.format(args.processdir, FINAL_FILE)
    command += ' -i {}/trimmed-{}'.format(args.processdir, master_audio_file)
    command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' {}/glued-{}'.format(args.processdir, FINAL_FILE)
    os.system(command)
    
main()
