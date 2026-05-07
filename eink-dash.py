from termcolor import colored
from dataclasses import dataclass
import os
import json5 as json
import subprocess
import tempfile
import shutil

# ==== Configuration ====


@dataclass
class Config:
    update_interval: int
    display_width: str
    display_height: str
    palette: [str]
    mqtt_broker: str
    mqtt_device_name: str


def load_config() -> Config:
    with open(os.path.join(os.path.dirname(__file__), "config.jsonc"), "r") as f:
        config_data = json.load(f)
    palette = config_data["palette"]
    if (
        not isinstance(palette, list)
        or not all(isinstance(color, str) for color in palette)
        or len(palette) != 4
    ):
        raise ValueError("Invalid palette in config.jsonc: must be a list of 4 strings")
    return Config(
        update_interval=config_data["update"].get("interval", 0),
        display_width=config_data["display_width"],
        display_height=config_data["display_height"],
        palette=palette,
        mqtt_broker=config_data["update"].get("mqtt_broker", ""),
        mqtt_device_name=config_data["update"].get("mqtt_device_name", ""),
    )


# ==== Rendering ====


def render_png(config: Config, output_path: str):
    res = subprocess.run(
        [
            "uv",
            "run",
            os.path.join(os.path.dirname(__file__), "dashboard/dashboard.py"),
            "--width",
            str(config.display_width),
            "--height",
            str(config.display_height),
            "--output",
            output_path,
        ]
    )
    if res.returncode != 0:
        raise RuntimeError(
            f"Failed to render dashboard, exited with code {res.returncode}"
        )


def dither_image(input_path: str, output_path: str, palette: [str]):
    dither_exe = shutil.which("dithers")
    if dither_exe is None:
        dither_exe = os.path.join(
            os.path.dirname(__file__), "dithers/target/release/dithers"
        )
        if os.name == "nt":
            dither_exe += ".exe"
        if not os.path.isfile(dither_exe):
            raise RuntimeError(
                f"dithers executable not found. Looked in PATH and at {dither_exe}. You may need to build it from the Rust source code."
            )
    res = subprocess.run(
        [
            dither_exe,
            input_path,
            output_path,
            *palette,
        ]
    )
    if res.returncode != 0:
        print(colored(f"Error dithering image: {res.stderr}", "red"))
        raise RuntimeError(f"Failed to dither image, exited with code {res.returncode}")


def output_to_eink_display(image_path: str):
    # not yet implemented
    pass


def render_dashboard(config: Config):
    print(colored("Rendering dashboard to PNG...", "blue"))
    work_dir = os.path.join(tempfile.gettempdir(), "eink-dash")
    os.makedirs(work_dir, exist_ok=True)
    image_path = os.path.join(work_dir, "dashboard.png")
    render_png(config, image_path)

    print(colored("Dithering image for e-ink display...", "blue"))
    dither_image(image_path, image_path, config.palette)

    print(colored("Outputting image to e-ink display...", "blue"))
    output_to_eink_display(image_path)

    print(colored("Done refreshing dashboard!", "green"))


# ==== Main ====


if __name__ == "__main__":
    try:
        config = load_config()
    except Exception as e:
        print(colored(f"Error loading config.jsonc: {e}", "red"))
        raise e

    args = [
        "uv",
        "run",
        os.path.join(os.path.dirname(__file__), "trigger/trigger.py"),
    ]
    if config.update_interval > 0:
        args += ["--interval", str(config.update_interval)]
    if config.mqtt_broker != "":
        args += ["--mqtt-broker", config.mqtt_broker]
    if config.mqtt_device_name != "":
        args += ["--mqtt-device-name", config.mqtt_device_name]
    trigger_proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
    )
    try:
        for line in iter(trigger_proc.stdout.readline, b""):
            print(colored(f"Trigger event: {line.decode().strip()}", "green"))
            try:
                render_dashboard(config)
            except Exception as e:
                print(colored(f"Error rendering dashboard: {e}", "red"))
    except KeyboardInterrupt:
        print(colored("Shutting down...", "yellow"))
        trigger_proc.terminate()
