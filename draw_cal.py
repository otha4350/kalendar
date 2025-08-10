from icalevents import icalevents, icalparser
import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor, features
import calendar
import datetime
import locale
import holidays
import numpy


# Constants for calendar layout
IMG_WIDTH = 800
IMG_HEIGHT = 480
CAL_X = 10
CAL_Y = 65
CAL_W = 800 - CAL_X * 2
CAL_H = 405
MAX_EVENTS = 5
FONT = ImageFont.truetype("font/Libre_Baskerville/LibreBaskerville-Italic.ttf", index=0, encoding="unic", layout_engine="raqm")
SYMBOL_FONT = ImageFont.truetype("font/dejavu-sans/ttf/DejaVuSans.ttf", index=0, encoding="unic", layout_engine="raqm", size=12)

c_black = "black"
c_white = "white"
c_yellow = "yellow"
c_red = "red"
c_blue = "blue"
c_green = "rgb(0, 255, 0)"



class DrawCalendarDay:
    def __init__(self, row, col, x, y, w, h, date: datetime.date):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.date = date 

    def draw(self, d: ImageDraw.ImageDraw, events: list[tuple[icalevents.Event, str]]):
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.w, self.y + self.h
        d.rectangle([x1, y1, x2, y2], outline=lines_color, width=1)

        
        # Draw date
        date_str = self.date.strftime("%a %d").capitalize()
        is_red_day = self.date.isoweekday() == 7 or self.date in holidays.Sweden()
        d.text((x1 + 5, y1 + 3),date_str, font=FONT, fill=weekday_color if not is_red_day else red_day_color)


        # Draw week number if it's Monday
        if self.date.isoweekday() == 1:
            week_str = "v. " + str(self.date.isocalendar().week)
            d.text((x2 - 5, y1 + 3), week_str, font=FONT, fill=weeknum_color, anchor="rt")

        # Draw events
        todays_events = []
        multiday_event_days = {}

        # Grab multiday events
        for event, color in events:
            if event.start.date() <= self.date <= event.end.date() and not event.start.date() == event.end.date() and not event.all_day:
                event_len = (event.end.date() - event.start.date()).days + 1
                event_day = (self.date - event.start.date()).days + 1
                event_day = f"({event_day}/{event_len})"
                multiday_event_days[event] = event_day
                todays_events.append((event, color))
            
        todays_oneday_events = [e for e in events if e[0].start.date() == self.date and not e[0] in multiday_event_days.keys()]
        todays_oneday_events.sort(key=lambda x: x[0].start)
        todays_events.extend(todays_oneday_events)

        events_today = len(todays_events)
        if events_today > MAX_EVENTS:
            todays_events = todays_events[:MAX_EVENTS-1]
        for idx, (event, color) in enumerate(todays_events):

            # draw bullet point
            bp = "★" if color == "#00FF00" else "❤" if color == "#FF0000" else "*"
            bp_w = d.textlength(bp, font=SYMBOL_FONT)

            event_text = ""
            if event in multiday_event_days.keys():
                event_text = event.summary
                days_string = multiday_event_days[event]
                unacceptable_textlen = lambda text: d.textlength(text + "..." + days_string, font=FONT) > self.w - (bp_w)
                if unacceptable_textlen(event_text):
                    while unacceptable_textlen(event_text):
                        event_text = event_text[:-1]
                    event_text += "..." + days_string
                else:
                    event_text += " " + days_string
            else:
                event_text = f"{event.start.strftime('%H')} {event.summary}" if not event.all_day else event.summary
                unacceptable_textlen = lambda text: d.textlength(text + "...", font=FONT) > self.w - (bp_w)
                if unacceptable_textlen(event_text):
                    while unacceptable_textlen(event_text):
                        event_text = event_text[:-1]
                    event_text += "..."
            
            length = d.textlength(event_text, font=FONT)
            bbox = (x1 + 2, y1 +3+ (12 * (idx+1)), min(x1 + 2 + length + bp_w, x2-1), y1 + (12 * (idx+2)) +1)
            d.rounded_rectangle(bbox,radius=3, fill=color)
            d.text((x1+2, y1 +3+ (12 * (idx+1)) - 2), bp, font=SYMBOL_FONT, fill="#FFFFFF")
            d.text((x1 + 2+bp_w, y1 +3+ (12 * (idx+1))), event_text, fill="#FFFFFF", font=FONT)

        
        if  events_today > MAX_EVENTS:
            d.text((x1 + 2, y2 - 15), f"+{events_today - MAX_EVENTS} till härligheter...", fill=lines_color, font=FONT, anchor="lt")
        
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
                    row=week_index,
                    col=day_index,
                    x=x + day_index * self.day_width,
                    y=y + week_index * self.week_height,
                    w=self.day_width,
                    h=self.week_height,
                    date=date,
                ))
            self.days_grid.append(week_row)

    def draw(self, d: ImageDraw.ImageDraw, events):
        # Draw background
        d.rectangle([self.x, self.y, self.x + self.w, self.y + self.h], fill="rgba(255,255,255,200)")

        for week in self.days_grid:
            for day in week:
                day.draw(d, events)
        for week_row in self.days_grid:
            for day in week_row:
                if day.date == datetime.date.today():
                    d.rectangle([day.x, day.y, day.x+day.w, day.y+day.h], outline=today_box_color, width=2)

        month_name = datetime.date.today().strftime("%B %Y").capitalize()
        month_font = ImageFont.truetype("font/Libre_Baskerville/LibreBaskerville-Italic.ttf", 60)
        d.text((400, 5), month_name, font=month_font, fill=month_color, anchor="mt")


def setup_image():
    ImageDraw.ImageDraw.fontmode = "L"
    image = Image.open("205988fgsdl.jpg").convert("RGB")
    resizedimage = image.resize((IMG_WIDTH, IMG_HEIGHT))

    out = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), (0, 0, 0, 0))
    out.paste(resizedimage, (0, 0))
    d = ImageDraw.Draw(out, "RGBA")
    return out, d

def  do_stuff():
    global background_color, weekday_color, weeknum_color, month_color, lines_color, today_box_color, red_day_color
    background_color = c_white
    weekday_color = c_black
    weeknum_color = c_red
    month_color = c_green
    lines_color = c_black
    today_box_color = c_red
    red_day_color = c_red

    locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")
    out, d = setup_image()
    cal = DrawCalendar(CAL_X, CAL_Y, CAL_W, CAL_H)

    events: list[tuple[icalevents.Event, str]] = []
    with open("calendars.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()
        for row in reader:
            
            es = icalevents.events(row[3], start=datetime.date.today() - datetime.timedelta(weeks=52), end=datetime.date.today() + datetime.timedelta(weeks=52))
            es = [(e, row[2]) for e in es]
            events.extend(es)

    cal.draw(d, events)
    return out

if __name__ == "__main__":
    global colors
    
    out = do_stuff()
    print(out.getcolors())


    palette_image = Image.new("P", (1, 1))
    #[(360588, 0), (10355, 1), (1488, 2), (9377, 3), (2192, 5)]
    palette_image.putpalette([255, 255, 255, 0, 0, 0, 255, 255, 0, 255, 0, 0, 0, 0, 255, 0, 255, 0])


    out = out.convert("RGB").quantize(6, palette=palette_image)
    out.show()
    # out.show()

    # DESATURATED_PALETTE = [
    #     [0, 0, 0],
    #     [255, 255, 255],
    #     [255, 255, 0],
    #     [255, 0, 0],
    #     [0, 0, 255],
    #     [0, 255, 0],
    #     [255, 255, 255]]

    # SATURATED_PALETTE = [
    #     [0, 0, 0],
    #     [161, 164, 165],
    #     [208, 190, 71],
    #     [156, 72, 75],
    #     [61, 59, 94],
    #     [58, 91, 70],
    #     [255, 255, 255]]
   
    # def _palette_blend(saturation, dtype="uint8"):
    #     saturation = float(saturation)
    #     palette = []
    #     for i in range(6):
    #         rs, gs, bs = [c * saturation for c in SATURATED_PALETTE[i]]
    #         rd, gd, bd = [c * (1.0 - saturation) for c in DESATURATED_PALETTE[i]]
    #         if dtype == "uint8":
    #             palette += [int(rs + rd), int(gs + gd), int(bs + bd)]
    #         if dtype == "uint24":
    #             palette += [(int(rs + rd) << 16) | (int(gs + gd) << 8) | int(bs + bd)]
    #     return palette
    
    # dither = Image.Dither.FLOYDSTEINBERG

    # # Image size doesn't matter since it's just the palette we're using
    # palette_image = Image.new("P", (1, 1))

    # if out.mode == "P":
    #     print("P")
    #     # Create a pure colour palette from DESATURATED_PALETTE
    #     palette = numpy.array(DESATURATED_PALETTE, dtype=numpy.uint8).flatten().tobytes()
    #     palette_image.putpalette(palette)

    #     # Assume that palette mode images with an unset palette use the
    #     # default colour order and "DESATURATED_PALETTE" pure colours
    #     if not out.palette.colors:
    #         out.putpalette(palette)

    #     # Assume that palette mode images with exactly six colours use
    #     # all the correct colours, but not exactly in the right order.
    #     if len(out.palette.colors) == 6:
    #         dither = Image.Dither.NONE
    # else:
    #     # All other image should be quantized and dithered
    #     palette = _palette_blend(0)
    #     palette_image.putpalette(palette)

    # image = out.convert("RGB").quantize(6, palette=palette_image, dither=dither)
    # image.show()

