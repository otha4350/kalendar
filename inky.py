
from inky.auto import auto
import draw_cal

if __name__ == "__main__":
    out = draw_cal.do_stuff()
    inky = auto(ask_user=True, verbose=True)
    resizedimage = out.resize(inky.resolution)
    inky.set_image(resizedimage)
    inky.show()
