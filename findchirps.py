#! /usr/bin/env python

import matplotlib
if __name__ == '__main__': matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np



"""
* Use cross correlation to find up and down chirps
#* Use the "clean" file to get the up and down and find the expected duration
* For each file, find the up and down peaks
#* If the duration is not very close to the clean one, raise a warning
* In the end, just output a file with video file name, up chrip location, and down chirp location
* We can tweak the numbers manually if we want
"""

UPCHIRP = 'up-long.wav'
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
    import scipy.signal as sps
    from tqdm import tqdm
    import os
    import glob
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()
    
    master_audio_file = 'master.wav'
    all_video_files = glob.glob('{}/*.mov'.format(args.processdir))
    all_video_files += glob.glob('{}/*.MOV'.format(args.processdir))
    all_video_files = [os.path.basename(f) for f in all_video_files]
    
    # Extract audio from all video files
    for video_file in all_video_files:
      video_file = video_file.strip()
      filename = '{}/{}'.format(args.processdir, video_file)
      assert os.path.exists(filename)
      basename = os.path.basename(filename)
      basename, _ = os.path.splitext(basename)
      command = 'ffmpeg -y -i {homedir}/{video} -vn -ar 44100 {homedir}/{basename}.wav'.format(homedir=args.processdir, video=video_file, basename=basename)
      os.system(command)
    
    UPFS, up = read_and_normalize_audio(UPCHIRP)

    audio_data = {}
    master_audio_file = master_audio_file.strip()
    results = {}
    
    #for audio_file in audio_files:
    for video_file in tqdm(all_video_files + [master_audio_file]):
        video_file = video_file.strip()
        basename = os.path.basename(video_file)
        basename, _ = os.path.splitext(basename)
        audio_file = '{}/{}.wav'.format(args.processdir, basename)
        FS, data = read_and_normalize_audio(audio_file)
        assert FS == UPFS
        audio_data[audio_file] = data
        
        if len(data.shape) > 1:
            data = data[:,0]
        upxcorr = sps.fftconvolve(data, up[::-1], mode='full')
        start_time = np.argmax(upxcorr)  / float(FS)
        basename = os.path.basename(audio_file)
        #plot_figure(upxcorr, downxcorr, audio_file)
        results[video_file] = start_time
    
    ofile = open('{}/{}'.format(args.processdir, OFILE), 'w')
    ofile.write(json.dumps(results, indent=4, sort_keys=True))
    ofile.close()
     


def plot_figure(upxcorr, downxcorr, audio_file):
    import os
    print 'Figure'
    plt.figure()
    plt.plot(upxcorr, label='Up')
    plt.plot(downxcorr, label='Down')
    plt.legend()
    plt.title(audio_file)
    
    print 'Saving'
    plt.savefig(os.path.splitext(audio_file)[0])
    plt.close()

   
main()
