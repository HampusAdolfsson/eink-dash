# trigger

This module is responsible for determining when to trigger an update of the eink
dashboard. This is done via a simple timer.

## Usage

Run the module:

```
uv run trigger.py --interval <seconds>
```
Where `<seconds>` is the interval at which to trigger updates. The default is 60 seconds.

When triggered, the module will print a single line of JSON to the console:

```json
{ "message": "update" }
```
