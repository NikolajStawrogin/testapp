"""Serve the learning app on this computer using Python's standard library."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
import webbrowser


def main():
    parser = argparse.ArgumentParser(description="Taipei kennen lokal starten")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Der Port muss zwischen 1 und 65535 liegen.")

    root = Path(__file__).resolve().parent
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as error:
        print(f"Der lokale Start auf Port {args.port} ist nicht möglich: {error}")
        print("Falls der Port belegt ist: python server.py --port 8766")
        return 1

    url = f"http://127.0.0.1:{args.port}/"
    print(f"Taipei kennen läuft lokal: {url}")
    print("Dieses Fenster geöffnet lassen. Beenden mit Strg+C.")
    if not args.no_browser:
        opener = Timer(0.2, webbrowser.open, args=(url,))
        opener.daemon = True
        opener.start()
    try:
        with server:
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nDie lokale App wurde beendet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
