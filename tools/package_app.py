"""Build and verify a complete local app ZIP using Python's standard library."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/stadt-kennen-v0.11.zip")
    parser.add_argument("--html", type=Path, help="Optional additional path for the standalone browser file")
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "tools/export_standalone.py")], check=True)
    names = [".gitignore", ".nojekyll", "GITHUB_PAGES.md", "index.html", "styles.css", "app.js", "street-map.js", "bootstrap.js", "region-ui.js", "REGIONEN.md", "server.py", "Start.bat",
             "README.md", "ANFORDERUNGEN.md", "KARTENQUELLE.md", "OFFIZIELLE_NAMEN.md", "THIRD_PARTY_NOTICES.md",
             "UMSETZUNGSPLAN.md", "PRUEFBERICHT.md", "Taipei-kennen.html"]
    paths = [ROOT / name for name in names]
    paths += sorted(path for path in (ROOT / "data").rglob("*") if path.is_file())
    paths += sorted((ROOT / "tests").glob("*.py"))
    paths += sorted((ROOT / "tools").glob("*.py"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, "taipei-kennen/" + path.relative_to(ROOT).as_posix())
    with ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Das Paket besteht die CRC-Prüfung nicht")
        for path in paths:
            if archive.read("taipei-kennen/" + path.relative_to(ROOT).as_posix()) != path.read_bytes():
                raise ValueError("Paketinhalt weicht ab: " + path.name)
    if args.html:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        if args.html.resolve() != (ROOT / "Taipei-kennen.html").resolve():
            shutil.copyfile(ROOT / "Taipei-kennen.html", args.html)
    print(f"Paket geprüft: {len(paths)} Dateien, {args.output.stat().st_size:,} Bytes, {args.output}")


if __name__ == "__main__":
    main()
