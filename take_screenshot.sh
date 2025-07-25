#!/bin/bash
source ~/.virtualenvs/pimoroni/bin/activate

firefox --headless --screenshot --window-size=800,480 "http://localhost:3001" -P "kalendar" -no-remote &
sleep 30
./image.py --file screenshot.png