
from inky.auto import auto
import draw_cal

if __name__ == "__main__":
    inky = auto(ask_user=True, verbose=True)

    out = draw_cal.draw_image()
    inky.set_image(out)
    inky.show()
