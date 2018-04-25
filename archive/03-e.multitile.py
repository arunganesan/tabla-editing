#! /usr/bin/env python

"""
Take the trimmed files.
Take input a list of video files and the master audio file.
For each video file, we will simply tile them in a pleasing way.
Then glue on audio track.
"""


def main():
    import argparse
    import scipy.signal as sps
    from tqdm import tqdm
    import os, json
    from readgrid import read_spec
    
    parser = argparse.ArgumentParser()
    parser.add_argument('processdir')
    args = parser.parse_args()
    
    
    specfile = '{}/gridspec.json'.format(args.processdir)
    assert os.path.exists(specfile)
    gridspec = read_spec(specfile)
    raw_GS = json.loads(open(specfile).read())
    WIDTH = raw_GS['width']
    HEIGHT = raw_GS['height']
    
    master_audio_file = 'cropped-master.wav'
    
    # Just convert to TS file
    all_video_files = gridspec.keys()
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        command = "ffmpeg -y"
        command += " -i {}/{} -an".format(args.processdir, video_file)
        command += " -q:v 4"
        command += " {}/{}.ts".format(args.processdir, basename)
        os.system(command)
    
    # Mosaic
    # https://trac.ffmpeg.org/wiki/Create%20a%20mosaic%20out%20of%20several%20input%20videos
    command = "ffmpeg -y"
    for video_file in all_video_files:
        basename, ext = os.path.splitext(video_file)
        filename = "{}/{}.ts".format(args.processdir, basename)
        command += " -i {} -an".format(filename)
    
    OFILE = 'mosaic.mp4'
    command += ' -filter_complex "'
    command += " nullsrc=size={}x{} [base];".format(WIDTH, HEIGHT)

    for idx, video_file in enumerate(all_video_files):
        cell_width = gridspec[video_file]['width']
        cell_height = gridspec[video_file]['height']
        command += ' [{idx}:v] setpts=PTS-STARTPTS, scale={w}:{h}:force_original_aspect_ratio=increase, crop={w}:{h}:(ow-iw)/2:(oh-ih)/2 [video-{idx}];'.format(idx=idx, w=cell_width, h=cell_height)
   

    for idx, video_file in enumerate(all_video_files):
        x = gridspec[video_file]['x']
        y = gridspec[video_file]['y']

        if idx == 0:
            command += ' [base][video-{c}] overlay=shortest=1:x={x}:y={y} [tmp{n}];'.format(c=idx, n=idx+1, x=x, y=y)
        elif idx == len(all_video_files) - 1:
            command += ' [tmp{c}][video-{c}] overlay=shortest=1:x={x}:y={y}'.format(c=idx, x=x, y=y)
        else:
            command += ' [tmp{c}][video-{c}] overlay=shortest=1:x={x}:y={y} [tmp{n}];'.format(c=idx, n=idx+1, x=x, y=y)
            
    command += ' "'
    command += ' -c:v libx264 {}/{}'.format(args.processdir, OFILE)
    os.system(command)
    

    # Glue audio file
    command = 'ffmpeg -y -i {}/{}'.format(args.processdir, OFILE)
    command += ' -i {}/{}'.format(args.processdir, master_audio_file)
    #command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' -shortest -c:v copy -c:a mp3 -b:a 256k'
    command += ' {}/glued-{}'.format(args.processdir, OFILE)
    os.system(command)
    
main()
