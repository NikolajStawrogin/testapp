# Prüfung der Straßen- und Menüerweiterung

Stand: 3. November 2026. Zielversion 0.7.

Der abschließende gemeinsame Lauf mit 36 Prüfungen ist bestanden (450,679 s): 29 Browserprüfungen und sieben Datenprüfungen. Nach der mobilen Sichtprüfung wurden Menübeschriftung und Aufgabenanzeige über der Karte verbessert; die vier betroffenen mobilen Bezirks-/Fluss-/Straßenprüfungen sind danach erneut bestanden (32,375 s und 41,734 s).

Die endgültige Browser-Einzeldatei wurde in einem isolierten Verzeichnis geprüft, das ausschließlich diese HTML-Datei enthielt. Alle drei zusätzlichen Prüfungen für ganze Straßen und Namensverdeckung, mobiles Straßenquiz sowie Lernstand-Export/Import sind bestanden (64,797 s). Der mobile Durchlauf war nach dem ersten Öffnen vollständig offline, einschließlich Zoom, Verschieben, Vorschau, Bestätigung, Rundenabschluss, Menü und Hilfe. JavaScript-Fehler und externe Laufzeitabrufe wurden nicht festgestellt. Die JavaScript-Syntaxprüfung und `git diff --check` sind ebenfalls bestanden.

Das lokale ZIP-Paket enthält 43 Dateien einschließlich Einzeldatei, Quellenarchiven, Datenskripten und Tests. `tools/package_app.py` hat die CRC-Prüfung bestanden und jeden archivierten Inhalt bytegenau mit seiner Quelldatei verglichen. Die Browser-Einzeldatei und das vollständige Paket sind jeweils etwa 21 MB groß. Git-interne Dateien und temporäre Entwicklungswerkzeuge sind nicht enthalten.

## Git-Zwischenstände

- `ad9b634`: bisherige geprüfte Bezirks-/Fluss-/Metro-App gesichert und gepusht.
- `b6d4ac5`: reproduzierbare Straßenquellen und Abdeckungsprüfungen gepusht.
- `088a2db`: Straßenlernen, Quiz, Navigation, Einstellungen und Lernstand-Sicherung gepusht.
- `1ea96cf`: ganze Straßen aus Sections, Schutz vor verräterischen Untereinheitsnamen und verbesserte mobile Aufgabenanzeige gepusht.

Für den geprüften Funktionsstand ergaben lokales `git rev-parse HEAD` und entferntes `git ls-remote origin refs/heads/main` identisch `1ea96cffabd99272a10b2911ff35a270bf28f433`. `git status --short --branch` zeigte anschließend keine offenen Änderungen. Die abschließende Dokumentation ergänzt diesen Stand; Anwendungscode und Daten bleiben dabei unverändert.

## Prüfumfang

- Alle 41 Bezirke, beide Städte, Flüsse und Metro bleiben nutzbar.
- Straßen-Erkundung, Lernkarten, Quiz, richtige/falsche Antwort, Fehlerwiederholung und Fortschritt.
- Stadt, Bezirke, Straßenklasse, Sections/Lanes/Alleys, Suche und einzelne Straßen.
- Zielnamen und zugängliche Kartennamen vor der Antwort verbergen; Orientierungsschalter geben keine Antworten ab.
- Ganze Straßeneinheiten per Maus hervorheben und wählen; Touch-Auswahl vor der Antwort bestätigen; an Kreuzungen zwischen nahen Verläufen wechseln.
- Touch-Zoom, Verschieben und abgebrochene Gesten geben keine versehentlichen Antworten ab.
- Ganze Straßen werden aus ihren Sections gebildet und bleiben zusätzlich zu einzelnen Sections wählbar. Beschriftungen untergeordneter Gassen verraten die übergeordnete Lösung nicht. Auf dem Handy stehen Aufgabe, Lösung und Weiter-Schaltfläche direkt über der Karte.
- Menü, mobile Navigation, Einstellungen, Hilfe, Verlaufssicherung, Importvalidierung und ausdrückliche Importbestätigung.
- Alte Lernstände und Einstellungen, Weiterverwendung nach Neuladen und Fortschrittslöschung.
- Reproduzierbare Quellenarchive, Hashes, eindeutige Aufgabenidentitäten, Geometrien und tatsächliche Abdeckung aller 41 Bezirke.
- Keine externen Laufzeitabrufe und keine JavaScript-Fehler während der Browserprüfungen.

## Grenzen der Aussage

Browserprüfungen laufen in Chromium einschließlich mobiler Touch-Emulation. Es ist damit kein Test auf jedem echten Android-/iOS-Gerät belegt. Die Einzeldatei wird isoliert über einen lokalen Testserver ohne weitere App-Dateien geprüft; die verwaltete Browserumgebung schränkt direkte `file://`-Navigation ein.

Die Datenprüfungen belegen den enthaltenen Bestand und seine Zuordnung, keine heutige amtliche Vollständigkeit. Geometrien außerhalb des Zentrums stammen aus einer 2021 versionierten Quelle, ergänzt um einen Innenstadt-Auszug von 2026. Englische Namen stammen aus dokumentierten Referenzen beziehungsweise aus regelbasierten numerischen Adresszusätzen; 1.363 wählbare Einheiten haben keine englische Zuordnung und werden standardmäßig nicht abgefragt. Aktueller Originalabgleich und abschließende Rechteprüfung vor öffentlicher Veröffentlichung bleiben offen.
