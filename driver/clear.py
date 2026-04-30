from PIL import Image
from waveshare_epd import epd7in5h


def main():
    try:
        display = epd7in5h.EPD()
        display.init()

        display.Clear()

        display.sleep()
    except Exception as e:
        epd7in5h.epdconfig.module_exit()
        raise e


if __name__ == "__main__":
    main()
