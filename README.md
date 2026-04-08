# Kalendar

A smart calendar application for Inky e-ink displays, featuring calendar events, weather forecasts, and customizable layouts.

## 📸 Preview

![Finished Calendar Display](./calendar-preview.jpg)

## Features

- **Multi-Color E-Ink Support** - Display on color-capable Inky displays (Red/Yellow/Blue variants)
- **Calendar Integration** - Import and display events from iCalendar (.ics) files
- **Weather Forecast** - Show current weather and forecasts with weather icons
- **Button Control** - Hardware button daemon for interactive control
- **Flexible Layouts** - Support for different view modes (week view, etc.)
- **Custom Fonts** - Includes DejaVu Sans, Garamond, Libre Baskerville, and Noto Sans fonts
- **Error Handling** - Graceful error display on the e-ink screen

## Requirements

- Inky display device 
- Raspberry Pi micro
- Python 3.7+

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:otha4350/kalendar.git
   cd kalendar
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your iCalendar file and weather configuration

## Usage

### Display Calendar on Inky
```bash
python show_on_inky.py
```

### Run Daemon Mode
Set a cron job at startup to run:
```bash
./start_daemon.sh
```

### Configuration

Edit `draw.json` to customize:
- Display mode (currently supports "week", "month")
- Additional display options

## Project Structure

```
.
├── draw_cal.py          # Main calendar drawing logic
├── show_on_inky.py      # Display controller for Inky devices
├── weather.py           # Weather integration and forecasting
├── button_daemon.py     # Hardware button event handler
├── draw.json            # Configuration file
├── start.sh             # Service startup script
├── start_daemon.sh      # Daemon startup script
├── font/                # Font files
│   ├── dejavu-sans/
│   ├── garamond/
│   ├── Libre_Baskerville/
│   └── noto-sans/
└── weather-icons/       # Weather icon assets
    ├── color/
    ├── fill-black/
    └── fill-white/
```

## Key Components

### draw_cal.py
Generates calendar images with events, weather, and custom layouts. Supports multiple color palettes for different e-ink display types.

### weather.py
Fetches and integrates weather data. Provides weather forecasts and icon selection.

### button_daemon.py
Handles hardware button inputs for navigation and control.

### show_on_inky.py
Interface between the calendar generator and the Inky display device.

## Display Specifications

- Resolution: 800 x 480 pixels
- Supports multi-color palettes (desaturated and saturated modes)
- Colors: Black, White, Yellow, Red, Blue, Green

## License

See individual font license files in the `font/` directory.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Troubleshooting

If the display shows errors, check:
1. Inky device is properly connected
2. All dependencies are installed
3. Calendar and weather data sources are accessible
4. Configuration in `draw.json` is valid

## Author
Otto Hammar

Created with ❤️ for e-ink display enthusiasts.
