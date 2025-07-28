
from inky.auto import auto
import draw_cal

if __name__ == "__main__":
    inky = auto(ask_user=True, verbose=True)
    draw_cal.background_color = inky.WHITE
    draw_cal.weekday_color = inky.GREEN
    draw_cal.weeknum_color = inky.BLUE
    draw_cal.month_color = inky.BLACK
    draw_cal.lines_color = inky.BLACK
    draw_cal.today_box_color = inky.RED

    out = draw_cal.do_stuff()
    # resizedimage = out.resize(inky.resolution)
    inky.set_image(out)
    inky.show()
