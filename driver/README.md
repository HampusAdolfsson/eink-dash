# driver

This modules is responsible for communicating with the e-ink display.
It currently only supports the 7.5 inch 4-color display, but can easily be extended to support other types of displays by replacing the `waveshare_epd` library.

## Usage

To show an image on the display:

```bash
uv run main.py <image_path>
```

To clear the display:

```bash
uv run clear.py
```
