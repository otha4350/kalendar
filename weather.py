# Import the module.
from datetime import datetime, timedelta
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Change this to your actual API key
with open("api_key.txt", "r") as f:
    YOUR_API_KEY = f.read().strip()
# Change this to your actual tier
YOUR_TIER = tiers.FREE

# Initialize the main Meteosource object

weather_dict = {
    1: 63,  # Not available
    2: 0,  # Sunny
    3: 4,  # Mostly sunny
    4: 4,  # Partly sunny
    5: 2,  # Mostly cloudy
    6: 8,  # Cloudy
    7: 8,  # Overcast
    8: 51,  # Overcast with low clouds
    9: 56,  # Fog
    10: 21,  # Light rain
    11: 22,  # Rain
    12: 20,  # Possible rain
    13: 11,  # Rain shower
    14: 14,  # Thunderstorm
    15: 15,  # Local thunderstorms
    16: 27,  # Light snow
    17: 28,  # Snow
    18: 26,  # Possible snow
    19: 34,  # Snow shower
    20: 31,  # Rain and snow
    21: 31,  # Possible rain and snow
    22: 32,  # Rain and snow
    23: 24,  # Freezing rain
    24: 11,  # Possible freezing rain
    25: 24,  # Hail
    26: 1,  # Clear (night)
    27: 5,  # Mostly clear (night)
    28: 7,  # Partly clear (night)
    29: 7,  # Mostly cloudy (night)
    30: 8,  # Cloudy (night)
    31: 8,  # Overcast with low clouds (night)
    32: 10,  # Rain shower (night)
    33: 15,  # Local thunderstorms (night)
    34: 35,  # Snow shower (night)
    35: 33,  # Rain and snow (night)
    36: 33,  # Possible rain and snow (night)
}


class CalWeather:
    def __init__(self):
        meteosource = Meteosource(YOUR_API_KEY, YOUR_TIER)
        self.forecast = meteosource.get_point_forecast(
            place_id="Uppsala",
            tz="Europe/Stockholm",
            lang="en",
            units="metric",
            sections=["current", "hourly", "daily"],
        )

    def get_image(self, w, h):
        # Create a blank image with white background
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))

        icon_img = Image.open(
            f"weather-icons/color/Weather Icon-{weather_dict[self.forecast.current.icon_num]}.png"
        ).convert("RGBA").resize((int(w*0.75),int(w*0.75)))
        img.paste(icon_img, (0, 0), icon_img)
        draw = ImageDraw.Draw(img)

        draw.text(
            (w, int(w*0.75)),
            f"{round(self.forecast.current.temperature)}°",
            font=ImageFont.truetype("font/noto-sans/NotoSans_Condensed-Bold.ttf", 75),
            fill="#FFFFFF",
            anchor="rb"
        )
        print(self.forecast.current.summary)

        font = ImageFont.truetype("font/noto-sans/NotoSans-Regular.ttf", 40)
        while draw.textlength(self.forecast.current.summary, font=font) > w - 10 and font.size > 10:
            font = font.font_variant(size=font.size - 1)
        draw.text(
            (5, h-40),
            f"{self.forecast.current.summary}",
            font=font,
            fill="#FFFFFF",
            anchor="lb"
        )
        img.show()
        return img


if __name__ == "__main__":

    w = CalWeather()
    img = w.get_image(190, 220)
    img.show()
