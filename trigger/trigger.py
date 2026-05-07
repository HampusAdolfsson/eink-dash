import argparse
import time
import ha_mqtt_discoverable as ha_mqtt
import ha_mqtt_discoverable.sensors as ha_sensors
import sys


def main():
    parser = argparse.ArgumentParser(description="Trigger script for eink-dash")
    parser.add_argument(
        "--interval", type=int, help="Update interval in minutes", default=0
    )
    parser.add_argument(
        "--mqtt-broker",
        type=str,
        help="MQTT broker address for Home Assistant",
        default="",
    )
    parser.add_argument(
        "--mqtt-device-name",
        type=str,
        help="Device name for MQTT discovery (default: E-Ink Dashboard)",
        default="E-Ink Dashboard",
    )
    args = parser.parse_args()

    if args.mqtt_broker != "":
        mqtt_settings = ha_mqtt.Settings.MQTT(host=args.mqtt_broker)
        device_info = ha_mqtt.DeviceInfo(
            name=args.mqtt_device_name, identifiers=["eink_dash_trigger"]
        )
        button_info = ha_sensors.ButtonInfo(
            name="Update Eink Dash",
            unique_id="eink_dash_update_button",
            device=device_info,
        )
        settings = ha_mqtt.Settings(mqtt=mqtt_settings, entity=button_info)
        update_button = ha_sensors.Button(
            settings,
            lambda client, userdata, msg: print('{"message": "update"}', flush=True),
        )
        update_button.write_config()
    elif args.interval <= 0:
        print(
            "No MQTT broker specified and interval is not set, so no updates will be triggered",
            file=sys.stderr,
        )
        return

    while True:
        if args.interval > 0:
            print('{"message": "update"}', flush=True)
            time.sleep(args.interval * 60)
        else:
            # Just sleep and let MQTT trigger updates
            time.sleep(60 * 60)


if __name__ == "__main__":
    main()
