import jinja2
from dataclasses import dataclass
import os
import sys

import json5 as json
import datetime
import shutil

import subprocess
import argparse


# ==== Configuration ====


@dataclass
class Config:
    time_format: str
    date_format: str
    output_path: str

    width: int
    height: int


def init_config() -> Config:
    """Initialize configuration from command-line arguments and config.jsonc"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default="dashboard.png", help="Output PNG file path"
    )
    parser.add_argument(
        "--width", default=800, type=int, help="Width of the output PNG"
    )
    parser.add_argument(
        "--height", default=480, type=int, help="Height of the output PNG"
    )
    args = parser.parse_args()

    try:
        with open(os.path.join(os.path.dirname(__file__), "config.jsonc")) as f:
            data = json.load(f)
            time_format = data.get("timeFormat", "%H:%M")
            date_format = data.get("dateFormat", "%Y-%m-%d")
    except Exception as e:
        raise RuntimeError(f"Error loading config.jsonc: {e}")

    return Config(
        time_format=time_format,
        date_format=date_format,
        output_path=args.output,
        width=args.width,
        height=args.height,
    )


# ==== Jinja -> HTML ====


def get_jinja_data(config: Config):
    """Get the variables to use to render the Jinja template"""

    now = datetime.datetime.now()

    return {
        "time": now.strftime(config.time_format),
        "date": now.strftime(config.date_format),
    }


def render_jinja_to_html(config: Config):

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "web"))
    )

    template = env.get_template("dashboard.html")

    rendered = template.render(get_jinja_data(config))
    return rendered


# ==== HTML -> PNG ====


def find_chromium_executable() -> str | None:
    """Find the path to the Chromium or Chrome executable"""

    which = shutil.which("chrome")

    if which is not None:
        return which


def render_html_to_png(html: str, config: Config):
    """Render the given HTML to a PNG file using headless Chromium"""
    chromium_path = find_chromium_executable()

    if chromium_path is None:
        raise RuntimeError("Could not find Chromium or Chrome executable")

    html_file = os.path.join(os.path.dirname(__file__), "web/rendered.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    args = [
        chromium_path,
        html_file,
        "--headless",
        f"--screenshot={os.path.join(os.getcwd(), config.output_path)}",
        f"--window-size={config.width},{config.height}",
        "--disable-gpu",
        "--no-sandbox",
    ]
    subprocess.run(args)

    os.remove(html_file)


# ==== Main ====


def main():

    try:
        config = init_config()

    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    try:
        html = render_jinja_to_html(config)

    except Exception as e:
        print(f"Error rendering Jinja template: {e}")
        sys.exit(1)

    try:
        render_html_to_png(html, config)

    except Exception as e:
        print(f"Error rendering HTML to PNG: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
