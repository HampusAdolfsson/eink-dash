# trigger

This module is responsible for determining when to trigger an update of the eink
dashboard. This can be done via Home Assistant or a timer.

## Usage

Run the module:

```
uv run trigger.py [options]
  --interval SECONDS  Interval in seconds for timer-based triggering (default: None)
  --mqtt-broker URL    MQTT broker URL for Home Assistant triggering (default: None)
```

When triggered, the module will print a single line of JSON to the console:

```json
{
    "message": "triggered",
    "reason": "home_assistant"  // or "timer"
}
```
