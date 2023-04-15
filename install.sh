#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: install.sh <folder_name>"
    exit 1
fi

path=$1

cp IndentOFX.py $path/
cp OFX.sublime-syntax $path/
