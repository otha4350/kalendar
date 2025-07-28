
from inky.auto import auto
import draw_cal

if __name__ == "__main__":
    inky = auto(ask_user=True, verbose=True)

    # 0 # black
    # 1 # white
    # 2 # yellow
    # 3 # red
    # 4 # blue
    # 5 # green

    draw_cal.background_color = 1  
    draw_cal.weekday_color = 5
    draw_cal.weeknum_color = 4
    draw_cal.month_color = 0
    draw_cal.lines_color = 0
    draw_cal.today_box_color = 5

    out = draw_cal.do_stuff()
    inky.set_image(out)
    inky.show()
