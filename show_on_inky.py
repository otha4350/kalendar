
from inky.auto import auto
import draw_cal


def show_on_inky(prev_image=None):

    inky = auto(ask_user=True, verbose=True)

    out = draw_cal.draw_image()
    if prev_image and out == prev_image:
        return
    inky.set_image(out)
    inky.show()


if __name__ == "__main__":
    show_on_inky()