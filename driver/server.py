import argparse
import http.server
import subprocess
import tempfile
import sys


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_PUT(self):
        try:
            content_length = int(self.headers["Content-Length"])
            content_type = self.headers["Content-Type"]
            if content_type == "image/png":
                extension = "png"
            elif content_type == "image/jpeg":
                extension = "jpg"
            else:
                extension = self.path.split(".")[-1]
            image_data = self.rfile.read(content_length)
        except Exception as e:
            self.send_error(400, str(e))

        with tempfile.NamedTemporaryFile(suffix=f".{extension}") as tmp_file:
            tmp_file.write(image_data)
            tmp_file.flush()

            res = subprocess.run(["uv", "run", "draw.py", tmp_file.name])
            if res.returncode != 0:
                print("Failed to update display", file=sys.stderr)
                self.send_error(500, "Failed to update display")
            else:
                self.send_response(200, "OK")
                self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Run the e-ink display server.")
    parser.add_argument("--port", type=int, default=80, help="Port to listen on")
    args = parser.parse_args()

    server_address = ("", args.port)
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
