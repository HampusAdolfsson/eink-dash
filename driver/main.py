import argparse
from PIL import Image
from waveshare_epd import epd7in5h


def main():
    parser = argparse.ArgumentParser(description="E-ink display driver")
    parser.add_argument("image_path", help="Path to the image to display")

    args = parser.parse_args()
    image = Image.open(args.image_path)
    try:
        display = epd7in5h.EPD()
        display.init()

        display.display(display.getbuffer(image))

        display.sleep()
    except Exception as e:
        epd7in5h.epdconfig.module_exit()
        raise e


if __name__ == "__main__":
    main()
