"""Export the learning app as one self-contained HTML file."""

import argparse
import json
from pathlib import Path
import re
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def local_resource(url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"Externe Ressource im Export nicht erlaubt: {url}")
    path = (ROOT / parsed.path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Ressource liegt außerhalb des Projekts")
    return path.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "Taipei-kennen.html")
    args = parser.parse_args()
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    scripts = []

    def inline_styles(match):
        css = local_resource(match.group(1))
        if "</style" in css.lower():
            raise ValueError("Unerwarteter Style-Abschluss in CSS")
        return "<style>\n" + css + "\n</style>"

    def collect_script(match):
        text = local_resource(match.group(1))
        text = re.sub(r"</script", lambda token: "<\\/" + token.group(0)[2:], text, flags=re.IGNORECASE)
        scripts.append(text)
        return ""

    html, style_count = re.subn(r'<link rel="stylesheet" href="([^"]+)">', inline_styles, html)
    html, script_count = re.subn(r'<script src="([^"]+)" defer></script>', collect_script, html)
    if style_count != 1 or script_count != 2:
        raise ValueError("Unerwartete Ressourcenliste; Export muss überprüft werden")
    paths = ["data/districts.js", "data/metro.js", "data/rivers.js", "data/streets.js", "data/street-parents.js", "data/duesseldorf.js", "data/levels-taipei.js", "data/levels-duesseldorf.js", "street-levels.js", "region-ui.js", "street-map.js", "app.js"]
    embedded = json.dumps({path:local_resource(path) for path in paths}, ensure_ascii=False, separators=(",", ":"))
    embedded = embedded.replace("<", "\\u003c")
    scripts.insert(0, "window.APP_EMBEDDED = " + embedded + ";")
    # Inline scripts run after the complete UI has been parsed; inline defer would not delay them.
    html = html.replace("</body>", "\n" + "\n".join("<script>\n" + text + "\n</script>" for text in scripts) + "\n</body>")
    html = html.replace('class="brand" href="index.html"', 'class="brand" href=""')
    html = html.replace("Originaldaten und Lizenzhinweis liegen im Ordner <code>data</code>.",
                        "Die verwendeten geografischen Daten sind in dieser HTML-Datei enthalten. Originaldaten und ausführliche Rechtehinweise sind zusätzlich im ZIP-Paket verfügbar.")
    html = html.replace("Herkunft und Bearbeitung sind in data/RIVERS-SOURCE.md dokumentiert.",
                        "Die bearbeiteten Flussflächen sind in dieser Datei enthalten; Originalauszug und ausführliche Herkunftshinweise liegen zusätzlich im ZIP-Paket.")
    html = html.replace("Herkunft und Abdeckungszahlen sind in data/STREETS-SOURCE.md und data/street-coverage.json dokumentiert.",
                        "Die Straßendaten sind in dieser Datei enthalten. Herkunft, Originalauszüge und Abdeckungsbericht sind zusätzlich im ZIP-Paket dokumentiert.")
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#315b45"/><text x="32" y="44" font-size="40" text-anchor="middle" fill="#d9eb96">北</text></svg>'
    html = html.replace("</head>", '<link rel="icon" href="data:image/svg+xml,' + quote(svg, safe="") + '">\n</head>')
    notice = "\n<!-- Self-contained browser edition. District geometry: g0v/twgeojson, CC0. Metro and street geography: copyright OpenStreetMap contributors, ODbL 1.0, https://opendatacommons.org/licenses/odbl/1-0/ . The geographic Metro and street databases embedded below are offered under ODbL 1.0. River areas: Taiwan Water Resources Agency; detailed source and name-reference notices are available in the Sources dialog and the full download package. -->\n"
    html = html.replace("<!doctype html>", "<!doctype html>" + notice)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"Browser-Datei erstellt: {args.output} ({args.output.stat().st_size} Bytes)")


if __name__ == "__main__":
    main()
