from icalevents import icalevents
import csv
from PIL import Image, ImageDraw, ImageFont, ImageColor, features
import calendar
import datetime
import locale
import holidays



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
c_green = "green"



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
        todays_events = [e for e in events if e[0].start.date() == self.date]
        todays_events.sort(key=lambda x: x[0].start)

        events_today = len(todays_events)
        if events_today > MAX_EVENTS:
            todays_events = todays_events[:MAX_EVENTS-1]
        for idx, (event, color) in enumerate(todays_events):

            bp = "★" if color == "5" else "❤" if color == "3" else "*"
            d.text((x1+2, y1 +3+ (12 * (idx+1)) - 2), bp, font=SYMBOL_FONT, fill=int(color))
            bp_w = d.textlength(bp, font=SYMBOL_FONT)


            event_text = f"{event.start.strftime('%H')} {event.summary}" if not event.all_day else event.summary
            unacceptable_textlen = lambda text: d.textlength(text + "...", font=FONT) > self.w - (bp_w)
            if unacceptable_textlen(event_text):
                while unacceptable_textlen(event_text):
                    event_text = event_text[:-1]
                event_text += "..."
            d.text((x1 + 2+bp_w, y1 +3+ (12 * (idx+1))), event_text, fill=int(color), font=FONT)
        
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
    out = Image.new("P", (IMG_WIDTH, IMG_HEIGHT), background_color)
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, IMG_WIDTH, IMG_HEIGHT], fill=background_color)
    return out, d

def do_stuff():
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

    events = []
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
    out.show()

