# A helper script to watch for changes to dashboard files and re-render the
# dashboard when changes are detected.

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess
import os


def normalize_path(path: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), path))


watched_files = [
    normalize_path("web/dashboard.html"),
    normalize_path("web/styles.css"),
    normalize_path("config.jsonc"),
    normalize_path("dashboard.py"),
]


def render_dashboard():
    args = [
        "uv",
        "run",
        "dashboard.py",
        "--output",
        "dashboard.png",
        "--width",
        "800",
        "--height",
        "480",
    ]
    subprocess.run(args)


class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        path = normalize_path(event.src_path)
        if path in watched_files:
            print("Re-rendering dashboard...")
            render_dashboard()


def main():
    render_dashboard()
    observer = Observer()
    handler = EventHandler()
    observer.schedule(handler, path=os.path.dirname(__file__), recursive=True)
    observer.start()
    print("Watching for changes...")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            break
    observer.join()


if __name__ == "__main__":
    main()
