#! /bin/bash

echo ./caption_maker.py $1
./caption_maker.py $1
echo ./crop_to_right_length.py $1
./crop_to_right_length.py $1
echo ./multitile.py $1
./multitile.py $1
echo ffmpeg -i glued-mosaic.mp4 -c:v libx264 -strict -2 -c:a aac -ar 44100 -r 30 -pix_fmt yuv420p -shortest 
ffmpeg -y -i $1/glued-mosaic.mp4 -c:v libx264 -strict -2 -c:a aac -ar 44100 -r 30 -pix_fmt yuv420p -shortest $1/final.mp4
