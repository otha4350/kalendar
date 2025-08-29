#!/bin/bash -x

git reset --hard origin/main
git clean -df
git pull

source ~/.virtualenvs/pimoroni/bin/activate
python ~/kalendar/show_on_inky.py