#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: install.sh <folder_name> where folder name in a path to your Sublime Plugins (check via Preferences -> Browse Packages...)"
    exit 1
fi

path=$1

cp indent_ofx.py $path/
cp Main.sublime-menu $path/
cp OFX.sublime-syntax $path/
