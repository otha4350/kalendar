#!/bin/bash
cargo run &
sleep 10

chromium-browser --headless --disable-gpu --screenshot=screenshot.png -window-size=800,480 "http://localhost:3001"

source ~/.virtualenvs/pimoroni/bin/activate
./image.py --file screenshot.png