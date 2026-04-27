import argparse
import time


def main():
    parser = argparse.ArgumentParser(description="Trigger script for eink-dash")
    parser.add_argument(
        "--interval", type=int, help="Update interval in seconds", default=60
    )

    args = parser.parse_args()

    while True:
        print('{"message": "update"}', flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
