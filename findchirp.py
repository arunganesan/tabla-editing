#! /usr/bin/env python
import matplotlib
if __name__ == '__main__': matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


from arunutils import dsp
from arunutils import audio

UPCHIRP = 'Up.wav'
DOWNCHIRP = 'Down.wav'

REF_AUDIO = 'mictrack.wav'

AUDIO_FILES = [
  REF_AUDIO,
  'dslr-audio-resampled.wav',
  'laptop-audio.wav',
  'phone-audio.wav'
]

def read_and_normalize_audio (audiofile):
  from scipy.io import wavfile
  rate, signal = wavfile.read(audiofile)
  converted = np.array(signal, dtype=np.float64)
  normalized = converted / np.amax(converted)
  return rate, normalized 



def main():
  import numpy as np
  import scipy.signal as sps
  from tqdm import tqdm
  import os

  UPFS, up = read_and_normalize_audio(UPCHIRP)
  DOWNFS, down = read_and_normalize_audio(DOWNCHIRP)
  assert UPFS == DOWNFS

  print 'Up={}, Down={}'.format(UPFS, DOWNFS)
  audio_data = {}
  for audio_file in tqdm(AUDIO_FILES):
    FS, data = read_and_normalize_audio(audio_file)
    assert FS == UPFS
    
    audio_data[audio_file] = data
    
    print 'Correlating. FS: {}'.format(FS) 
    #upxcorr = np.correlate(data, up, mode='full')
    #downxcorr = np.correlate(data, down, mode='full')
    if len(data.shape) > 1:
        data = data[:,0]
    upxcorr = sps.fftconvolve(data, up[::-1], mode='full')
    downxcorr = sps.fftconvolve(data, down[::-1], mode='full')
    
    start_time = np.argmax(upxcorr)  / float(FS)
    ATLEAST = int((67 + start_time)*FS)
    end_time = (ATLEAST + np.argmax(downxcorr[ATLEAST:])) / float(FS)
    duration = end_time - start_time
    print '{}) {} - {}. Len = {}'.format(audio_file, start_time, end_time, duration)
    plot_figure(upxcorr, downxcorr, audio_file)
     


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
