# driver

This module contains the code that *needs* to run on the Raspberry Pi to drive the e-ink display.
It uses the `waveshare_epd` library to communicate with the display.
It currently only supports the 7.5 inch 4-color display, but can easily be extended to support other types of displays by replacing the `waveshare_epd` library.

## Usage

To show an image on the display:

```bash
uv run draw.py <image_path>
```

To clear the display:

```bash
uv run clear.py
```

The `server.py` file runs a simple HTTP server that listens for PUT requests
containing an image. When an image is received, it is displayed on the e-ink
display.

```bash
uv run server.py --port <port_number>
```
Where `<port_number>` is the port on which the server will listen for incoming requests. The default is 80.

You can send an image to the server using `curl`:

```bash
curl http://<ip_address>:<port_number>/ --upload-file <image_path>
```
