# ============================================================
#  🐉 HERE BE DRAGONS
# ============================================================
#  You don't need to understand this file — just run it!
#
#  What it's doing:
#    Python can act as a web server — a program that "serves"
#    web pages to a browser, just like a real website. This
#    script starts a tiny server on your own computer at
#    localhost:8000, then uses the webbrowser module to open
#    explorer.html automatically.
#
#    It also uses threading to keep the server running in the
#    background while the rest of the script finishes. These
#    are advanced Python concepts well beyond the workshop.
#
#  To launch the Music Data Explorer:
#      python3 data/explorer.py
# ============================================================

import http.server
import os
import threading
import webbrowser
from pathlib import Path

PORT = 8000
DIR  = Path(__file__).parent


class _Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIR), **kwargs)

    def log_message(self, *_):
        pass  # keep the terminal quiet


if __name__ == "__main__":
    os.chdir(DIR)
    url = f"http://localhost:{PORT}/explorer.html"

    with http.server.HTTPServer(("", PORT), _Handler) as httpd:
        print(f"Music Data Explorer → {url}")
        print("Press Ctrl+C to stop.\n")
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
