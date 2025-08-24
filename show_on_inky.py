
from inky.auto import auto
import draw_cal
import gpiod
import gpiodevice
from gpiod.line import Bias, Direction, Value


LED_PIN = 13

# Find the gpiochip device we need to blink the led, we'll use
# gpiodevice for this, since it knows the right device
# for its supported platforms.
chip = gpiodevice.find_chip_by_platform()

# Setup for the LED pin
led = chip.line_offset_from_id(LED_PIN)
gpio = chip.request_lines(consumer="inky", config={led: gpiod.LineSettings(direction=Direction.OUTPUT, bias=Bias.DISABLED)})

def show_on_inky(prev_image=None):
    gpio.set_value(led, Value.ACTIVE)

    inky = auto(ask_user=True, verbose=True)

    out = draw_cal.draw_image()
    if prev_image and out == prev_image:
        gpio.set_value(led, Value.INACTIVE)
        return
    inky.set_image(out)
    inky.show()
    gpio.set_value(led, Value.INACTIVE)


if __name__ == "__main__":
    show_on_inky()