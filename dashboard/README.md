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

- `time`: The current time
- `date`: The current date

[`config.jsonc`](config.jsonc) configures the Jinja variables (such as the time
and date formats). See the comments in the file for details.

## Development

To help with development, you can watch the dashboard files and automatically re-render the dashboard when they change:

```bash
uv run watch.py
```
