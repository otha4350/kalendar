# Import the module.
from datetime import datetime, timedelta
from pymeteosource.api import Meteosource
from pymeteosource.types import tiers
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from translate import Translator
import random

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
    12: 16,  # Possible rain
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

        summary = self.forecast.current.summary
        translator = Translator(to_lang="sv")
        summary_sv = translator.translate(summary)

        font = ImageFont.truetype("font/noto-sans/NotoSans_Condensed-Bold.ttf", 40)
        while draw.textlength(summary_sv, font=font) > w - 10 and font.size > 10:
            font = font.font_variant(size=font.size - 1)
        draw.text(
            (5, h-50),
            summary_sv,
            font=font,
            fill="#FFFFFF",
            anchor="lb"
        )

        for i in range(4):
            hour_idx = (i+1) * 3
            mini_img = self.get_mini_image(int(w/4), 50, hour_idx)
            img.paste(mini_img, (i * int(w/4), h - 50), mini_img)

        return img
    
    def get_mini_image(self, w, h, hour_idx):
        fc = self.forecast.hourly[hour_idx]
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        text_img = Image.new("P", (w, h), "#111111")
        text_draw = ImageDraw.Draw(text_img)
        draw = ImageDraw.Draw(img)
        
        icon_scale = 0.75
        icon_w, icon_h = int(w*icon_scale),int(w*icon_scale)
        icon_x, icon_y = int(w*((1-icon_scale)/2)), 5

        draw.ellipse([icon_x, icon_y, icon_x+icon_w,icon_y+icon_h], fill="white")

        bubble_size = 20
        rand_x = random.randrange(round(w/2-bubble_size/3), round(w/2+bubble_size/3)) - round(bubble_size/2)
        draw.ellipse([rand_x, 0, rand_x+bubble_size, bubble_size], fill="white")
        
        rand_x = random.randrange(round(w/2-bubble_size/3), round(w/2+bubble_size/3)) - round(bubble_size/2)
        draw.ellipse([rand_x, h-bubble_size, rand_x+bubble_size, h], fill="white")

        icon_img = Image.open(
            f"weather-icons/color/Weather Icon-{weather_dict[fc.icon]}.png"
        ).convert("RGBA").resize((icon_w, icon_h))
        img.paste(icon_img, (icon_x, icon_y), icon_img)
        
        


        text_draw.text(
            (int(w/2),5),
            f"{fc.date.strftime('%H')}",
            font=ImageFont.truetype("font/noto-sans/NotoSans_Condensed-Bold.ttf", 10),
            fill="#000000",
            anchor="mt"
        )

        text_draw.text(
            (int(w/2),h-10),
            f"{round(fc.temperature)}°",
            font=ImageFont.truetype("font/noto-sans/NotoSans_Condensed-Bold.ttf", 10),
            fill="#000000",
            anchor="mt"
        )
        img = Image.composite(img, text_img.convert("RGBA"), text_img.convert("L").point(lambda x: 255 if x == 17 else 0))
        return img
    
    def get_micro_image(self, w, h, date, color="fill-black"):
        fc = None
        for pfc in self.forecast.daily:
            fmt = lambda dt: datetime.strftime(dt, "%Y-%m-%d")
            if fmt(pfc.day)==fmt(date):
                fc = pfc
                break
        
        if fc is None:
            return Image.new("RGBA", (w, h), (255, 255, 255, 0))

        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))

        draw = ImageDraw.Draw(img)
        
        draw.ellipse([0,0,w-1,h-1], fill="white")

        icon_img = Image.open(
            f"weather-icons/{color}/Weather Icon-{weather_dict[fc.icon]}.png"
        ).convert("RGBA").resize((w-2,h-2))

        if color == "color":
            icon_img = ImageEnhance.Brightness(icon_img).enhance(0.8)

        img.paste(icon_img, (1,1), icon_img)

        if color == "fill-black":
            img = ImageEnhance.Contrast(img).enhance(2)

        return img


if __name__ == "__main__":

    w = CalWeather()

    # w.get_mini_image(int(190/4), 60, 3)
    img = w.get_micro_image(16,16, datetime.now())

    img.show()
