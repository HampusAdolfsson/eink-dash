# dashboard

This module renders the dashboard itself from Jinja-templated HTML and CSS, and
then renders that to a PNG using headless Chromium/Chrome.

## Usage

```bash
uv run dashboard.py --output <output_file>.png --width <width> --height <height>
```

The script expects `chrome` to be in the system PATH.

## Configuration

The dashboard is configured by [`dashboard.html`](dashboard.html) and
[`config.jsonc`](config.jsonc).

[`dashboard.html`](dashboard.html) is a Jinja template that defines the layout
and styling of the dashboard. See the [Jinja
documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/) for how to
use Jinja templating syntax. The following variables are available in the Jinja template:

- `now`: The current date and time as a `datetime` object
- `weather`: A dictionary containing:
    - `temperature`: The current temperature
    - `weather_code`: The current weather code (see [Open-Meteo documentation](https://open-meteo.com/en/docs#weather_variable_documentation) for details)
- `forecast_daily`: A list of dictionaries for the next few days, each containing:
    - `date`: The date of the forecast (a `date`)
    - `temperature_max`: The maximum temperature for the day
    - `temperature_min`: The minimum temperature for the day
    - `weather_code`: The weather code for the day (see [Open-Meteo documentation](https://open-meteo.com/en/docs#weather_variable_documentation) for details)
    - `sunrise`: The sunrise time for the day (a `datetime`)
    - `sunset`: The sunset time for the day (a `datetime`)
- `forecast_hourly`: A list of dictionaries for the next 16 hours, each containing:
    - `time`: The time of the forecast (a `datetime`)
    - `temperature`: The temperature at that time
    - `precipitation`: The precipitation at that time
- `precipitation_description`: A natural language string describing today's precipitation

The following custom filters are also available:

- `weather_icon`: Takes a weather condition (a [`Kind`](https://python-weather.readthedocs.io/en/latest/forecast/weather.html#python_weather.enums.Kind)) and returns the corresponding icon filename.

[`config.jsonc`](config.jsonc) configures the Jinja variables. See the comments in the file for details.

## Development

To help with development, you can watch the dashboard files and automatically re-render the dashboard when they change:

```bash
uv run watch.py
```
