#! /bin/bash

echo ./findchirps.py $1
./findchirps.py $1
echo ./trim $1
./trim_glue.py $1
