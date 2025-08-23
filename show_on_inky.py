
from inky.auto import auto
import draw_cal

def show_on_inky():
    inky = auto(ask_user=True, verbose=True)

    out = draw_cal.draw_image()
    inky.set_image(out)
    inky.show()

if __name__ == "__main__":
    show_on_inky()