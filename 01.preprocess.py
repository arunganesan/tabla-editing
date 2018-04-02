#! /usr/bin/env python

"""
* Extract audio
* Resample audio to 44100 hertz
"""

def main():
    import argparse
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
    
    import subprocess
    # Resample videos
    for video_file in all_video_files:
        video_file = video_file.strip()
        filename = '{}/{}'.format(args.processdir, video_file)
        assert os.path.exists(filename)
        basename = os.path.basename(filename)
        basename, _ = os.path.splitext(basename)
        command = 'avconv -i {homedir}/{video} -vn -ar 44100 {homedir}/{basename}.wav'.format(homedir=args.processdir, video=video_file, basename=basename)
        os.system(command)
        
main()
