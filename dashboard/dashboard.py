import jinja2
from dataclasses import dataclass
import os
import open_meteo

import json5 as json
import datetime
import shutil

import subprocess
import argparse


# ==== Configuration ====


@dataclass
class Config:
    lat: float
    lon: float

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
            lat = data["lat"]
            lon = data["lon"]
    except Exception as e:
        raise RuntimeError(f"Error loading config.jsonc: {e}")

    return Config(
        lat=lat,
        lon=lon,
        output_path=args.output,
        width=args.width,
        height=args.height,
    )


# ==== Jinja -> HTML ====


async def get_jinja_data(config: Config):
    """Get the variables to use to render the Jinja template"""

    async with open_meteo.OpenMeteo() as meteo:
        forecast = await meteo.forecast(
            latitude=config.lat,
            longitude=config.lon,
            current_weather=True,
            daily=[
                open_meteo.DailyParameters.SUNRISE,
                open_meteo.DailyParameters.SUNSET,
                open_meteo.DailyParameters.TEMPERATURE_2M_MAX,
                open_meteo.DailyParameters.TEMPERATURE_2M_MIN,
                open_meteo.DailyParameters.WEATHER_CODE,
                open_meteo.DailyParameters.PRECIPITATION_SUM,
            ],
            hourly=[
                open_meteo.HourlyParameters.TEMPERATURE_2M,
                open_meteo.HourlyParameters.PRECIPITATION,
                open_meteo.HourlyParameters.WEATHER_CODE,
            ],
        )
        # Open-Meteo returns timezone-naive datetimes in UTC, so we
        # need to convert them to local time.
        def to_local_time(dt: datetime.datetime) -> datetime.datetime:
            return dt.replace(tzinfo=datetime.UTC).astimezone()

        daily = []
        for i in range(len(forecast.daily.time)):
            daily.append(
                {
                    "date": forecast.daily.time[i],
                    "temperature_max": forecast.daily.temperature_2m_max[i],
                    "temperature_min": forecast.daily.temperature_2m_min[i],
                    "weather_code": forecast.daily.weathercode[i],
                    "sunrise": to_local_time(forecast.daily.sunrise[i]),
                    "sunset": to_local_time(forecast.daily.sunset[i]),
                }
            )

        hourly = []
        now = datetime.datetime.now(datetime.UTC)
        for i in range(len(forecast.hourly.time)):
            local_time = to_local_time(forecast.hourly.time[i])
            if local_time < now:
                continue
            if local_time > now + datetime.timedelta(hours=16):
                break
            hourly.append(
                {
                    "time": local_time,
                    "temperature": forecast.hourly.temperature_2m[i],
                    "precipitation": forecast.hourly.precipitation[i],
                    "weather_code": forecast.hourly.weather_code[i],
                }
            )

    return {
        "now": now.astimezone(),
        "weather": forecast.current_weather,
        "forecast_daily": daily,
        "forecast_hourly": hourly,
        "precipitation_description": describe_precipitation(forecast.daily, forecast.hourly)
    }


def weather_code_to_icon(kind: int) -> str:
    """Convert a weather code to an icon filename"""

    mapping = {
        0: "sunny.png",
        1: "sunny.png",
        2: "partly_cloudy.png",
        3: "cloudy.png",
        45: "cloudy.png",
        48: "cloudy.png",
        51: "showers.png",
        53: "showers.png",
        55: "rain.png",
        56: "showers.png",
        57: "showers.png",
        61: "showers.png",
        63: "rain.png",
        65: "rain.png",
        66: "showers.png",
        67: "rain.png",
        71: "snow.png",
        73: "snow.png",
        75: "snow.png",
        77: "snow.png",
        80: "showers.png",
        81: "showers.png",
        82: "rain.png",
        85: "snow.png",
        86: "snow.png",
        95: "thunderbolt.png",
        96: "rain.png",
        99: "rain.png",
    }
    if kind not in mapping:
        print(f"Unknown weather kind: {kind}")

    return "icons/" + mapping.get(kind, "unknown.png")

def precipitation_type(kind: int) -> str | None:
    """Convert a weather code to a precipitation type name"""
    if kind in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "rain"
    if kind in [71, 73, 75, 77, 85, 86]:
        return "snow"
    return None

def kinds_to_precipitation(kinds: list[int]) -> set[str]:
    """Convert a list of weather codes to a set of precipitation type names"""
    precip_types: set[str] = set()
    for code in kinds:
        precip_type = precipitation_type(code)
        if precip_type is not None:
            precip_types.add(precip_type)
    return precip_types

def describe_precipitation(fdaily: open_meteo.DailyForecast, fhourly: open_meteo.HourlyForecast) -> str:
    """ Describes today's precipitation in natural language """
    if fdaily.precipitation_sum[0] == 0:
        expected_precip_type = fdaily.temperature_2m_max[0] < 0 and "snow" or "rain"
        return f"No {expected_precip_type} today!"

    precip_types = kinds_to_precipitation(fhourly.weather_code).union(kinds_to_precipitation([fdaily.weathercode[0]]))
    if len(precip_types) == 0:
        print("Warning: precipitation sum is non-zero, but no precipitation types found in hourly or daily forecast.")
        precip_types.add("rain")

    MORNING_END = 12
    AFTERNOON_END = 18

    precip_times = []
    day_end_idx = next((i for i, time in enumerate(fhourly.time) if time.date() > fhourly.time[0].date()), len(fhourly.time))
    todays_precipitation = zip(fhourly.precipitation[:day_end_idx], fhourly.time[:day_end_idx])
    if any(time.hour < MORNING_END and precip > 0 for precip, time in todays_precipitation):
        precip_times.append("morning")
    if any(time.hour >= MORNING_END and time.hour < AFTERNOON_END
           and precip > 0 for precip, time in todays_precipitation):
        precip_times.append("afternoon")
    if any(time.hour >= AFTERNOON_END and precip > 0 for precip, time in todays_precipitation):
        precip_times.append("evening")

    return f"{fdaily.precipitation_sum[0]} mm of {"/".join(precip_types)} today ({", ".join(precip_times)})."


async def render_jinja_to_html(config: Config):

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "web"))
    )
    env.filters["weather_icon"] = weather_code_to_icon

    template = env.get_template("dashboard.html")

    rendered = template.render(await get_jinja_data(config))
    return rendered


# ==== HTML -> PNG ====


def find_chromium_executable() -> str | None:
    """Find the path to the Chromium or Chrome executable"""

    candidates = ["chromium", "chromium-browser", "chrome"]
    for candidate in candidates:
        which = shutil.which(candidate)
        if which is not None:
            return which

    return None


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
        "--hide-scrollbars",
    ]
    subprocess.run(args)

    os.remove(html_file)


# ==== Main ====


async def main():

    try:
        config = init_config()

    except Exception as e:
        print(f"Configuration error: {e}")
        raise e

    try:
        html = await render_jinja_to_html(config)

    except Exception as e:
        print(f"Error rendering Jinja template: {e}")
        raise e

    try:
        render_html_to_png(html, config)

    except Exception as e:
        print(f"Error rendering HTML to PNG: {e}")
        raise e


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
