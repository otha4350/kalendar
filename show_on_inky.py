
from inky.auto import auto # pyright: ignore[reportMissingImports]
import draw_cal


def show_on_inky(prev_image=None):

    inky = auto(ask_user=True, verbose=True)

    try:
        out = draw_cal.draw_image()
    except Exception as e:
        out = draw_cal.draw_error(str(e))
    
    if prev_image and out == prev_image:
        return
    inky.set_image(out)
    inky.show()


if __name__ == "__main__":
    show_on_inky()