# Regionen und Düsseldorf-Erweiterung

## Ziel und akzeptierter Umfang

Einstieg: Stadt wählen → Thema wählen → Entdecken, Lernkarten oder Quiz. Die bisherigen beiden taiwanischen Städte bleiben eine gemeinsame Lernregion. Düsseldorf ist eine eigene Region mit deutschen Originalnamen, 50 Stadtteilen und zehn Stadtbezirken als getrennt wählbaren Gebietsebenen. Auch Straßen, Rhein und weitere Flüsse sowie Stadtbahn sollen dieselben Auswahl-, Beschriftungs-, Lern-, Quiz- und Fortschrittsfunktionen erhalten. Die Browser-App bleibt lokal lauffähig, ohne Konto, API-Schlüssel oder kostenpflichtigen Dienst.

## Aktueller Zwischenstand und offene Voraussetzung

Stadtauswahl, gezieltes Laden der jeweiligen regionalen Daten, beide Düsseldorfer Gebietsebenen und 2.891 benannte Straßen- und Wegeeinheiten sind umgesetzt. Alle 50 Stadtteile besitzen Straßeneinträge. Fluss- und Stadtbahndaten sind noch nicht enthalten: Der Zugriff auf die Originalquellen wird von der Netzwerkpolitik der laufenden Cloud-Umgebung mit 403 verweigert. Diese Themen bleiben im Düsseldorfer Zwischenstand deaktiviert und werden ausdrücklich als ausstehend bezeichnet. Das ist kein abgeschlossener Funktionsumfang.

Ein gespeicherter Konfigurationsentwurf ergänzt ausschließlich `opendata.duesseldorf.de`, `www.duesseldorf.de` und `overpass-api.de`. Das Konfigurationstool meldet `status: saved` und `requires_publish: true`. Der Nutzer muss die Änderungen in den Umgebungseinstellungen prüfen und speichern und anschließend die Umgebung veröffentlichen. Erst ein erfolgreicher Abruf belegt, dass die Änderung in dieser Sitzung wirkt.

Nach Freigabe:

1. `PYTHONPATH=/tmp/duesseldorf-deps python tools/collect_duesseldorf_data.py` sammelt Straßen mit OSM-Straßenklasse, benannte Gewässer und U-Linien samt Geometrien. Originalantwort, Abfrage, Zeitstempel und SHA-256 bleiben erhalten. Der Live-Abruf ist bisher nicht ausgeführt oder als erfolgreich getestet.
2. `PYTHONPATH=/tmp/duesseldorf-deps python tools/build_duesseldorf_data.py` erzeugt das lokale Regionalpaket neu. Die Alternative für dauerhaftes Setup ist eine eigene Python-Umgebung mit `shapely==2.1.2`; `/tmp` ist nicht als dauerhafte Installation vorausgesetzt.
3. Datenabdeckung, reale Linien/Flüsse, beide Gebietsebenen, Quiz, Touch, Speicherung, Import/Export und Offline-Einzeldatei prüfen; Dokumentation und Paket aktualisieren; committen und pushen.

## Datenbasis des Zwischenstands

- Stadtteile: OSM-Auszug aus Click That ’Hood, festgehaltener Repository-Commit `48ba05ad4c6969e3b3c25735492169227ae411f1`, mit GeoJSON-Zeitstempeln vom Juni 2015. Die Metadaten nennen OpenStreetMap als Herkunft. Die zehn Stadtbezirke werden aus der festen Stadtteilzuordnung vereinigt; es werden keine frei gezeichneten Grenzen verwendet.
- Straßen: zehn Qualitätsdateien des OSM-basierten Projekts `ckrey/stressmap`, Commit `78230754655af475a492de0af267722869d3afe1` vom 23. März 2023. Der tatsächliche OSM-Datenstand kann älter sein. Namen und Geometrien sind enthalten, Straßenklassen fehlen. Deshalb bleiben diese Einheiten ausdrücklich „Ohne Straßenklasse“; Fahrradqualitätswerte werden nicht als Straßenhierarchie ausgegeben.
- Alle benannten Quellverläufe innerhalb der Stadtgrenze werden je Name zusammengeführt. Benannte Wege sind eingeschlossen. Teilstücke außerhalb der Stadtgrenze werden entfernt. Kreuzt eine Straße mehrere Stadtteile oder Stadtbezirke, gehört sie zu jeder betroffenen Gebietsauswahl.
- Rohdaten liegen unter `data/duesseldorf/`. `source-manifest.json` hält unveränderliche Quell-URLs und SHA-256 fest. `coverage.json` zählt die Abdeckung pro Stadtteil. Keine Zusage aktueller amtlicher Vollständigkeit.
- Geodaten: © OpenStreetMap contributors, ODbL 1.0. Erläuterungen und Quellen stehen auch im Düsseldorfer Quellen-Dialog. Beim geplanten Overpass-Auszug werden Fluss-Mittellinien zu angenäherten sichtbaren Flächen gepuffert; diese sind keine vermessenen Ufergrenzen.

## Gemeinsame Funktionen und Bestandsschutz

`bootstrap.js` zeigt zunächst die Stadtauswahl. Mit `?region=taipei` bzw. `?region=duesseldorf` wird nur das benötigte regionale Datenpaket geladen. `region-ui.js` lokalisiert die Oberfläche; `app.js` und `street-map.js` bleiben gemeinsame Lern- und Kartenlogik. Unbekannte Regionen führen sicher zur Stadtauswahl.

Die alten Schlüssel `taipei-kennen.settings.v1` und `taipei-kennen.progress.v1` bleiben erhalten. Düsseldorf verwendet `duesseldorf-kennen.settings.v1` und `duesseldorf-kennen.progress.v1`. Es gibt keine automatische Vermischung oder Überschreibung zwischen Städten. Neue Sicherungen enthalten die Region; alte Sicherungen ohne Region werden weiterhin als Taipei-Sicherungen erkannt. Ein Import in die falsche Region wird vor der Übernahme abgewiesen.

Bei einer erneuten bewussten Stadtauswahl werden zunächst die Themen gezeigt. Ein Neuladen innerhalb einer Region kann die zuletzt gespeicherte Ansicht wiederherstellen. Gebietsebene und Gebietsauswahl sind während laufender Runden gesperrt.

Die Offline-Einzeldatei enthält beide regionalen Datenpakete und sämtliche Skripte. Der Starter wählt intern das gewünschte Paket, ohne Dateinachladen oder Netzwerkaufrufe. Die ZIP-Ausgabe enthält zusätzlich Quellen, Datengeneratoren, Herkunftshinweise und Tests.
