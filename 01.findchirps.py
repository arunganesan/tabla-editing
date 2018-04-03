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
DOWNCHIRP = 'down-long.wav'
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
    
    master_audio_file = lines[0]
    all_video_files = lines[1:]
    
    # Extract audio from all video files
    for video_file in all_video_files:
      video_file = video_file.strip()
      filename = '{}/{}'.format(args.processdir, video_file)
      assert os.path.exists(filename)
      basename = os.path.basename(filename)
      basename, _ = os.path.splitext(basename)
      command = 'avconv -i {homedir}/{video} -vn -ar 44100 {homedir}/{basename}.wav'.format(homedir=args.processdir, video=video_file, basename=basename)
      os.system(command)
    
    UPFS, up = read_and_normalize_audio(UPCHIRP)
    DOWNFS, down = read_and_normalize_audio(DOWNCHIRP)
    assert UPFS == DOWNFS

    audio_data = {}
    master_audio_file = master_audio_file.strip()
    results = []
    
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
        downxcorr = sps.fftconvolve(data, down[::-1], mode='full')
        start_time = np.argmax(upxcorr)  / float(FS)
        ATLEAST = 0 #int((67 + start_time)*FS)
        end_time = (ATLEAST + np.argmax(downxcorr[ATLEAST:])) / float(FS)
        duration = end_time - start_time
        
        
        basename = os.path.basename(audio_file)
        plot_figure(upxcorr, downxcorr, audio_file)
        results.append([video_file, start_time, end_time, duration])
    
    ofile = open('{}/{}'.format(args.processdir, OFILE), 'w')
    for result in results:
        ofile.write(' '.join(map(str, result)) +  '\n')
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
