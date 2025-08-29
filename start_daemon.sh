#!/bin/bash

git reset --hard origin/master
git clean -df
git pull

source ~/.virtualenvs/pimoroni/bin/activate
python ~/kalendar/button_daemon.py