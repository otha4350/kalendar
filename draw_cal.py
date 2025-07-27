from icalevents import icalevents
import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor, features
import calendar
import datetime
import locale

from inky.auto import auto

# Constants for calendar layout
IMG_WIDTH = 800
IMG_HEIGHT = 480
CAL_X = 50
CAL_Y = 70
CAL_W = 700
CAL_H = 400
FONT = ImageFont.truetype("font/Libre_Baskerville/LibreBaskerville-Regular.ttf", index=0, encoding="unic")
print(features.check_feature("raqm"))
PALETTE_COLORS = [
    "#1c181c", # background
    "#ffffff", # white
    "#1dad23", # green
    "#1e1dae", # blue
    "#cd2425", # red
    "#e7de23", # yellow
    "#d87b24", # orange
]

BACKGROUND_COLOR = "#ffffff"
WEEKDAY_COLOR = "#1c181c"
WEEKNUM_COLOR = "#1e1dae"
MONTH_COLOR = "#1c181c"
LINES_COLOR = "#1c181c"
TODAY_BOX_COLOR = "#1e1dae"



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
        d.rectangle([x1, y1, x2, y2], outline=LINES_COLOR, width=1)
        
        # Draw date
        d.text((x1 + 5, y1 + 5), self.date.strftime("%a %d").capitalize(), font=FONT, fill=WEEKDAY_COLOR)

        if self.date == datetime.date.today():
            d.rectangle([x1+1, y1+1, x2-1, y2-1], outline=TODAY_BOX_COLOR, width=2)

        # Draw week number if it's Monday
        if self.date.isoweekday() == 1:
            week_str = "v. " + str(self.date.isocalendar().week)
            d.text((x2 - 5, y1 + 5), week_str, font=FONT, fill=WEEKNUM_COLOR, anchor="rt")

        # Draw events
        todays_events = [e for e in events if e[0].start.date() == self.date]
        for idx, (event, color) in enumerate(todays_events):


            event_text = f"⬤{event.start.strftime('%H')} {event.summary}" if not event.all_day else event.summary
            if d.textlength(event_text + "...", font=FONT) > self.w - 10:
                while d.textlength(event_text + "...", font=FONT) > self.w - 10:
                    event_text = event_text[:-1]
                event_text += "..."

            d.text((x1 + 5, y1 + (20 * (idx+1))), event_text, fill=color, font=FONT)

        



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


        self.days_grid = []
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
        for week in self.days_grid:
            for day in week:
                day.draw(d, events)

        month_name = datetime.date.today().strftime("%B %Y").capitalize()
        month_font = ImageFont.truetype("font/Libre_Baskerville/LibreBaskerville-Italic.ttf", 60)
        d.text((400, 5), month_name, font=month_font, fill=MONTH_COLOR, anchor="mt")


def setup_image():
    out = Image.new("P", (IMG_WIDTH, IMG_HEIGHT), "#ffffff")
    color_tuples = [ImageColor.getrgb(c) for c in PALETTE_COLORS]
    palette = []
    for t in color_tuples:
        palette.extend(t)
    out.putpalette(palette)
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, IMG_WIDTH, IMG_HEIGHT], fill=BACKGROUND_COLOR)
    return out, d



if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")
    out, d = setup_image()
    cal = DrawCalendar(CAL_X, CAL_Y, CAL_W, CAL_H)

    events = []
    with open("calendars.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()
        for row in reader:
            
            es = icalevents.events(row[3], start=datetime.date.today() - datetime.timedelta(days=60), end=datetime.date.today() + datetime.timedelta(days=60))
            es = [(e, row[2]) for e in es]
            events.extend(es)

    cal.draw(d, es)

    inky = auto(ask_user=True, verbose=True)
    inky.set_image(out)
    inky.show()
