#!/bin/bash

git reset --hard origin/main
git clean -df
git pull

source ~/.virtualenvs/pimoroni/bin/activate
python ~/kalendar/button_daemon.py