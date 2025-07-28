
from inky.auto import auto
import draw_cal

if __name__ == "__main__":
    inky = auto(ask_user=True, verbose=True)

    draw_cal.c_black = 0
    draw_cal.c_white = 1
    draw_cal.c_yellow = 2
    draw_cal.c_red = 3
    draw_cal.c_blue = 4
    draw_cal.c_green = 5

    out = draw_cal.do_stuff()
    inky.set_image(out)
    inky.show()
