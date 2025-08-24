from icalevents import icalevents
import csv
from PIL import Image, ImageDraw, ImageFont
import calendar
import datetime
import locale
import holidays
import random
import os
from hyphen import Hyphenator, textwrap2
import json

# Constants for calendar layout
IMG_WIDTH = 800
IMG_HEIGHT = 480
CAL_X = 20
CAL_Y = 65
CAL_W = 800 - CAL_X * 2
CAL_H = 395
MAX_EVENTS = 5
BG_OPACITY = 0  # 0-255
FONT = ImageFont.truetype("font/dejavu-sans/ttf/DejaVuSans.ttf", index=0, encoding="unic", layout_engine="raqm", size=12)
LARGE_FONT = ImageFont.truetype("font/dejavu-sans/ttf/DejaVuSansCondensed.ttf", index=0, encoding="unic", layout_engine="raqm", size=21)
SYMBOL_FONT = ImageFont.truetype("font/dejavu-sans/ttf/DejaVuSans.ttf", index=0, encoding="unic", layout_engine="raqm", size=12)

c_black = "#000000"
c_white = "#FFFFFF"
c_yellow = "#FFFF00"
c_red = "#FF0000"
c_blue = "#0000FF"
c_green = "#00FF00"

DESAT_PALETTE = [
        0x1c, 0x18, 0x1c, #black
        0xff, 0xff, 0xff, #white
        0xe7, 0xde, 0x23, #yellow
        0xcd, 0x24, 0x25, #red
        0x1e, 0x1d, 0xae, #blue
        0x1d, 0xad, 0x23, #green
        ]
SAT_PALETTE = [ 0, 0, 0, 
                255, 255, 255, 
                255, 255, 0, 
                255, 0, 0, 
                0, 0, 255, 
                0, 255, 0]

def draw_text_with_bg(d, text_d, text, x, y, font, fill=c_black, bg_color=c_white, padding=1, antialias=False):
    text_draw = d if antialias else text_d

    length_px = text_draw.textlength(text, font=font)
    bbox = (x, y, x + length_px + padding * 2, y + font.size + padding * 2)
    d.rounded_rectangle(bbox, radius=3, fill=bg_color)
    text_draw.text((x + padding, y + padding), text, font=font, fill=fill)

def draw_text_with_outline(d, text_d, text, x, y, font, fill=c_black, outline_color=c_white, outline_width=1, anchor="lt"):
    # Draw outline
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                text_d.text((x + dx, y + dy), text, font=font, fill=outline_color, anchor=anchor)
    # Draw main text
    text_d.text((x, y), text, font=font, fill=fill, anchor=anchor)

def get_todays_events(events, date: datetime.date):
    todays_events = []
    multiday_event_days = {}

    # Grab multiday events
    for event, color in events:
        if event.start.date() <= date <= event.end.date() and not event.start.date() == event.end.date() and not event.all_day:
            event_len = (event.end.date() - event.start.date()).days + 1
            event_day = (date - event.start.date()).days + 1
            event_day = f"({event_day}/{event_len})"
            multiday_event_days[event] = event_day
            todays_events.append((event, color))
        
    todays_oneday_events = [e for e in events if e[0].start.date() == date and not e[0] in multiday_event_days.keys()]
    todays_oneday_events.sort(key=lambda x: x[0].start)
    todays_events.extend(todays_oneday_events)

    return todays_events, multiday_event_days

class DrawCalendarDay:
    def __init__(self, x, y, w, h, date: datetime.date):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.date = date 

    def draw(self, d: ImageDraw.ImageDraw, text_d: ImageDraw.ImageDraw, events: list[tuple[icalevents.Event, str]]):
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.w, self.y + self.h
        d.rectangle([x1, y1, x2, y2], outline=lines_color, width=1)

        
        # Draw date
        date_str = self.date.strftime("%a %d").capitalize()
        is_red_day = self.date.isoweekday() == 7 or self.date in holidays.Sweden()
        draw_text_with_bg(d, text_d, date_str, x1 + 3, y1 + 3, FONT, fill=weekday_color if not is_red_day else red_day_color, bg_color=c_white, padding=1)


        # Draw week number if it's Monday
        if self.date.isoweekday() == 1:
            week_str = "v. " + str(self.date.isocalendar().week)
            draw_text_with_bg(d, text_d, week_str, x2 - text_d.textlength(week_str, font=FONT)-5, y1 + 3, FONT, fill=weeknum_color, bg_color=c_white, padding=1)

        # Draw events
        
        todays_events, multiday_event_days = get_todays_events(events, self.date)

        events_today = len(todays_events)
        if events_today > MAX_EVENTS:
            todays_events = todays_events[:MAX_EVENTS-1]

        line_idx = 0
        for (event, color) in (todays_events):
            line_idx += 1

            # draw bullet point
            bp = "★" if color == "#00FF00" else "❤" if color == "#FF0000" else "*"
            bp_w = text_d.textlength(bp, font=SYMBOL_FONT)

            event_text = ""
            if event in multiday_event_days.keys():
                event_text = event.summary
                days_string = multiday_event_days[event]
                unacceptable_textlen = lambda text: text_d.textlength(text + "…" + days_string, font=FONT) > self.w - (bp_w)
                # unacceptable_textlen = lambda text: False
                if unacceptable_textlen(event_text):
                    while unacceptable_textlen(event_text):
                        event_text = event_text[:-1]
                    event_text += "…" + days_string
                else:
                    event_text += " " + days_string
            else:
                event_text = f"{event.start.astimezone().strftime('%H')} {event.summary}" if not event.all_day else event.summary
                unacceptable_textlen = lambda text: text_d.textlength(text + "…", font=FONT) > self.w - (bp_w)
                # unacceptable_textlen = lambda text: False
                if unacceptable_textlen(event_text):
                    while unacceptable_textlen(event_text):
                        event_text = event_text[:-1]
                    event_text += "…"
            
            length = text_d.textlength(event_text, font=FONT)
            bbox = (x1 + 2, y1 +3+ (12 * (line_idx)), min(x1 + 2 + length + bp_w, x2-1), y1 + (12 * (line_idx+1)) +4)
            d.rounded_rectangle(bbox,radius=3, fill=c_white)
            text_d.text((x1+2, y1 +3+ (12 * (line_idx)) - 2), bp, font=SYMBOL_FONT, fill=color)
            text_d.text((x1 + 2+bp_w, y1 +3+ (12 * (line_idx))), event_text, fill=c_black, font=FONT)

        if  events_today > MAX_EVENTS:
            draw_text_with_bg(d, text_d, f"+{events_today - MAX_EVENTS} till härligheter…", x1 + 2, y2 - 10-2, FONT.font_variant(size=10), fill=lines_color, bg_color=c_white, padding=0)
        
class DrawCalendar:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.locale_cal = calendar.LocaleTextCalendar(calendar.MONDAY, "sv-se")

        monthdates = self.locale_cal.monthdatescalendar(datetime.date.today().year, datetime.date.today().month)

        self.week_num = len(monthdates)
        self.day_width = w / 7
        self.week_height = h / self.week_num


        self.days_grid : list[list[DrawCalendarDay]]= []
        for week_index, week in enumerate(monthdates):
            week_row = []
            for day_index,date in enumerate(week):
                week_row.append(DrawCalendarDay(
                    x=x + day_index * self.day_width,
                    y=y + week_index * self.week_height,
                    w=self.day_width,
                    h=self.week_height,
                    date=date,
                ))
            self.days_grid.append(week_row)

    def draw(self, d: ImageDraw.ImageDraw, text_d: ImageDraw.ImageDraw, events):
        # Draw background
        d.rectangle([self.x, self.y, self.x + self.w, self.y + self.h], fill=f"rgba(255,255,255,{BG_OPACITY})")

        for week in self.days_grid:
            for day in week:
                day.draw(d,text_d, events)
        for week_row in self.days_grid:
            for day in week_row:
                if day.date == datetime.date.today():
                    d.rectangle([day.x, day.y, day.x+day.w, day.y+day.h], outline=today_box_color, width=2)

        month_name = datetime.date.today().strftime("%B %Y").capitalize()
        month_font = ImageFont.truetype("font/Libre_Baskerville/LibreBaskerville-Italic.ttf", 60)
        # text_d.text((400, 5), month_name, font=month_font, fill=month_color, anchor="mt")
        draw_text_with_outline(d, text_d, month_name, self.x + self.w / 2, 5, month_font, fill=month_color, outline_color=month_outline_color, outline_width=1, anchor="mt")

class DrawWeekDay:
    def __init__(self, x, y, w, h, date: datetime.date):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.date = date

    def draw(self, d: ImageDraw.ImageDraw, text_d: ImageDraw.ImageDraw, events):
        d.rectangle([self.x, self.y, self.x + self.w, self.y + self.h], outline=lines_color, width=1)
        ordinal = "a" if self.date.day <= 2 else "e"
        date_str = self.date.strftime(f"%A den %d:{ordinal} %B").capitalize()
        if self.date.day == 13 and self.date.isoweekday() == 5:
            date_str = "Fredagen den 13:e " + self.date.strftime("%B")

        is_red_day = self.date.isoweekday() == 7 or self.date in holidays.Sweden()
        text_width = text_d.textlength(date_str, font=FONT)
        draw_text_with_bg(d, text_d, date_str, self.x + self.w/2 - text_width/2, self.y + 3, FONT, fill=weekday_color if not is_red_day else red_day_color, bg_color=c_white, padding=1)

        todays_events, multiday_event_days = get_todays_events(events, self.date)

        line_idx = 0
        for event, color in todays_events:
            bp = "★" if color == "#00FF00" else "❤" if color == "#FF0000" else "*"

            event_text = event.summary
            if event in multiday_event_days.keys():
                event_text += " " + multiday_event_days[event]
            elif event.all_day:
                event_text = event.summary
            else:
                event_text = f"{event.start.astimezone().strftime('%H:%M')} {event_text}"
        
            event_text = bp  + event_text

            wrapped_lines = []

            max_width = int(self.w)
            while True:
                hyphenator = Hyphenator("sv_SE")
                wrapped_lines = textwrap2.wrap(event_text, max_lines = 4,width=max_width, break_long_words=True, use_hyphenator=hyphenator)
                lines_good = all([text_d.textlength(line, font=LARGE_FONT) <= self.w for line in wrapped_lines])
                if lines_good:
                    break
                max_width -= 1

            for line in wrapped_lines:
                line_idx += 1
                draw_text_with_bg(d, text_d, line, self.x + 2, self.y + 3 + (LARGE_FONT.size * (line_idx)), LARGE_FONT, fill=color, bg_color=c_white, padding=0, antialias=True)
            text_d.text((self.x + 2, self.y + 3 + (LARGE_FONT.size * (line_idx))), line, fill=color, font=LARGE_FONT)


class DrawWeek:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, d: ImageDraw.ImageDraw, text_d: ImageDraw.ImageDraw, events):
        # Draw background
        d.rectangle([self.x, self.y, self.x + self.w, self.y + self.h], fill=f"rgba(255,255,255,{BG_OPACITY})")

        # Draw day boxes, in a 4x2 grid
        day_width = self.w / 4
        day_height = self.h / 2

        for i in range(7):
            day_x = self.x + (i % 4) * day_width
            day_y = self.y + (i // 4) * day_height
            day = DrawWeekDay(
                x=day_x,
                y=day_y,
                w=day_width,
                h=day_height,
                date=datetime.date.today() + datetime.timedelta(days=i)
            )
            day.draw(d, text_d, events)

def setup_image():
    ImageDraw.ImageDraw.fontmode = "1"
    # get a random image in the wallpapers folder
    # wallpapers = [f for f in os.listdir("wallpapers") if f.endswith((".jpg", ".png"))]
    # random_wallpaper = random.choice(wallpapers)
    # out = Image.open(os.path.join("wallpapers", random_wallpaper)).convert("RGB")
    out = Image.open("20250214_082939112_iOS.jpg").convert("RGB")

    out = out.resize((IMG_WIDTH, IMG_HEIGHT))

    text_image = Image.new("P", (IMG_WIDTH, IMG_HEIGHT), color="#111111")
    text_d = ImageDraw.Draw(text_image)

    d = ImageDraw.Draw(out, "RGBA")
    return out, d, text_image, text_d

def draw_image():
    global background_color, weekday_color, weeknum_color, month_color, month_outline_color, lines_color, today_box_color, red_day_color
    background_color = c_white
    weekday_color = c_black
    weeknum_color = c_red
    month_color = c_white
    month_outline_color = c_black
    lines_color = c_black
    today_box_color = c_red
    red_day_color = c_red

    locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")
    

    events: list[tuple[icalevents.Event, str]] = []
    with open("calendars.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()
        for row in reader:
            fix_apple = row[3].startswith("webcal://")
            es = icalevents.events(row[3], start=datetime.date.today() - datetime.timedelta(weeks=52), end=datetime.date.today() + datetime.timedelta(weeks=52), fix_apple=fix_apple)
            es = [(e, row[2]) for e in es]
            events.extend(es)

    out, d, text_image, text_d = setup_image()
    if os.path.exists("draw.json"):
        with open("draw.json", "r") as f:
            data = json.load(f)
        option = data.get("draw_option", "month")
    else:
        option = ""

    if option not in ["month", "week"]:
        option = "month"
        with open("draw.json", "w") as f:
            json.dump({"draw_option": "month"}, f)

    if option == "month":
        cal = DrawCalendar(CAL_X, CAL_Y, CAL_W, CAL_H)
        cal.draw(d,text_d, events)
    elif option == "week":
        cal = DrawWeek(20, 20, IMG_WIDTH - 40, IMG_HEIGHT - 40)
        cal.draw(d,text_d, events)
            

    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette(DESAT_PALETTE)

    out = Image.composite(out, text_image.convert("RGBA"), text_image.convert("L").point(lambda x: 255 if x == 17 else 0)) #17 is #111111, the bg of text image
    out = out.convert("RGB")
    out = out.quantize(6, palette=palette_image)
    out.putpalette(SAT_PALETTE)

    return out

if __name__ == "__main__":
    global colors
    
    out = draw_image()
    out.putpalette(DESAT_PALETTE)
    out.show()