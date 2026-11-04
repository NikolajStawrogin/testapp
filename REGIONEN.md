# Regionen und Düsseldorf-Erweiterung

## Umfang und Bedienung · 0.14

Einstieg: Stadt wählen → Thema → Gebiet → Lernweise/Level → Kartenhilfen → bestätigen → separate Spielansicht. Die Karte erscheint erst nach Bestätigung; Einstellungen stehen nicht mehr links neben der Karte. Siehe GEFUEHRTER_EINSTIEG.md. Taipei/New Taipei bleiben eine gemeinsame Lernregion. Düsseldorf verwendet deutsche Originalnamen. Quiz und Gebietsauswahl verwenden die 50 Stadtteile alphabetisch nach Namen wie Eller oder Wersten. Enthalten sind 2.891 benannte Straßen-/Wegeeinheiten und sechs Gewässer: Rhein, Düssel, Nördliche Düssel, Südliche Düssel, Itter und Kittelbach.

Das Feld über der Karte bietet „Ganz Düsseldorf“ und die 50 Stadtteilnamen. Die darunterliegende Liste erlaubt mehrere Stadtteile für eine gemeinsame Runde. Nummerierte Stadtbezirke sind keine auswählbare Quiz-Ebene mehr. Ihre Geometrien und frühere Lernergebnisse bleiben als Bestandsdaten erhalten. Alte ausgewählte Stadtbezirke werden in ihre zugehörigen Stadtteile übersetzt.

Die Flüsse lassen sich einzeln mitüben, gemeinsam mit Gebieten oder als reine Flussrunde. Flussflächen und Namen sind unabhängig schaltbar; die gesuchte Bezeichnung bleibt bis zur Auflösung verborgen. Richtige und falsche Antworten, Fehlerwiederholung, Lernkarten und Lernstand verwenden dieselben Funktionen wie bei Taipei.

Als Orientierung stehen 26 Linien aus dem archivierten VRR-Bestand bereit: zwölf U-Bahn-/Stadtbahnlinien, sechs S-Bahnlinien, sieben Straßenbahnlinien und SkyTrain. Die vier Bahnarten sind einzeln schaltbar; die Auswahl wird gespeichert. Die Legende startet geschlossen. Bahnlinien sind **schematische Verbindungen zwischen belegten Haltestellen**, keine exakten Gleiskurven. Farben kennzeichnen Verkehrsarten; S-Bahn und SkyTrain haben zusätzliche Strichmuster. Es handelt sich um einen Datenstand, keinen aktuellen Fahrplan und keine Zusage vollständiger aktueller Betriebsdaten.

Die Browser-App bleibt lokal lauffähig, ohne Konto, API-Schlüssel oder kostenpflichtigen Dienst. Alle Geodaten liegen lokal. Die zunächst blockierten Originalabrufe sind für diese Version keine Voraussetzung mehr: Die fehlenden Ebenen wurden aus separat veröffentlichten, fest versionierten Datenarchiven aufgebaut. Es ist keine weitere Freigabe durch den Nutzer nötig.

## Oberflächensprachen

Beide Regionen und die Stadtauswahl verwenden dieselbe Umschaltung zwischen 國語 (traditionelle Zeichen) und Englisch. Erststart ist 國語, die gespeicherte Auswahl gilt regionsübergreifend. Kartennamen bleiben separat einstellbar. Siehe [SPRACHEN.md](SPRACHEN.md).

## Straßen-Level

Beide Regionen verwenden standardmäßig Level mit je zehn neuen ganzen Straßen. Die Reihenfolge basiert auf geschätzter Länge innerhalb des gewählten Gebiets; jede Gebietsauswahl behält ihre eigene Level-Position. Berechnung, Wiederholung und Grenzen stehen in [STREET_LEVELS.md](STREET_LEVELS.md). Die Metadaten werden offline aus denselben Straßengeometrien abgeleitet. Es gibt keine zusätzliche Karten-API oder laufenden Dienst.

## Datenquellen und Grenzen

- **Stadtteile:** OSM-Auszug aus Click That ’Hood, Commit `48ba05ad4c6969e3b3c25735492169227ae411f1`, GeoJSON-Zeitstempel Juni 2015. Zehn Stadtbezirke werden aus der festen Stadtteilzuordnung vereinigt; keine frei gezeichneten Grenzen.
- **Straßen:** zehn OSM-basierte Qualitätsdateien aus `ckrey/stressmap`, Commit `78230754655af475a492de0af267722869d3afe1` vom 23. März 2023. Der tatsächliche OSM-Datenstand kann älter sein. Namen und Geometrien sind enthalten, Straßenklassen fehlen. Deshalb bleiben diese Einheiten ausdrücklich „Ohne Straßenklasse“. Fahrradqualität wird nicht als Straßenhierarchie ausgegeben. Benannte Wege sind eingeschlossen; alle 50 Stadtteile besitzen Einträge. Das ist kein aktuell amtlich geprüftes Straßenverzeichnis und keine Vollständigkeitszusage.
- **Gewässer:** `3ddruck12/flowtrail-pegel`, Commit `93b556e4314df05c6b2e887bc13721cb468f5ab2`, Datei `osm-waterways.geojson`, Auszugsversion 27.05.2026. Enthält ausdrücklich OSM-Flüsse und Kanäle mit ODbL-Hinweis. Für diese App werden benannte Flüsse innerhalb der Stadtgrenze vereinigt; sehr kurze Randfragmente unter 400 Metern entfallen. Die blauen Flächen sind angenäherte Puffer um echte Mittellinien, keine vermessenen Ufer. Kleine Bäche sind im Quellauszug nicht vollständig enthalten. Ortsbeschreibungen nennen die größten Überschneidungen mit den Stadtteilflächen.
- **Verkehr:** VRR-GTFS-Haltestellen und geordnete Haltefolgen, Version 25.08.2026, archiviert in `n3koBomb/linienblick`, Commit `b71ba453fb72696120ae591caeacae074768d6d2`. Verarbeitet werden nur U- und S-Bahn, reguläre Straßenbahnlinien und SkyTrain mit passenden Düsseldorfer Haltestellen. Doppelte Betreiberkennungen derselben Liniennummer und identische Verbindungen werden zusammengeführt. Busse, RE/RB und E-Sonderlinien sind nicht Teil dieser Orientierungsebene. Die Originaldateien enthalten keine GTFS-Shapes; die App kennzeichnet die schematische Darstellung ausdrücklich.
- **Nutzungsrechte:** OSM-Geodaten © OpenStreetMap contributors, ODbL 1.0. VRR wird als Datenherausgeber genannt. Der im Manifest verlinkte Verkehrsverbund-Katalog nennt für den offiziellen VRR-GTFS-Bestand CC BY ohne Versionsangabe; eine bestimmte Lizenzversion wird nicht erfunden. Die archivierte Originalquellen- und Katalogreferenz stehen im Datenpaket. Es wurde kein fremder App-Code übernommen.

Originalkopien, unveränderliche Quell-URLs und SHA-256 stehen unter `data/duesseldorf/`. `source-manifest.json` dokumentiert Gebiete/Straßen, `layers-source-manifest.json` Gewässer/Verkehr. Die Flussquelle wird verlustfrei und reproduzierbar mit gzip gespeichert. `coverage.json` zählt die Abdeckung.

## Reproduzieren und aktualisieren

Entwicklungsabhängigkeit: `shapely==2.1.2` in einer eigenen Python-Umgebung installieren. Die fertige App benötigt kein Python-Paket.

1. `python tools/build_duesseldorf_layers.py` prüft die archivierten Quell-Hashes und erzeugt Fluss- und Bahn-Ebenen ohne Netzwerkzugriff.
2. `python tools/build_duesseldorf_data.py` erzeugt das vollständige regionale Datenpaket samt Gebietszuordnung und Abdeckung.
3. `python -m unittest discover -s tests -v` prüft die Anwendung. Browserprüfungen benötigen Playwright und Chromium.
4. `python tools/export_standalone.py` erzeugt die selbstständige Browserdatei; `python tools/package_app.py` baut und prüft das vollständige ZIP mit Quellen und Tests.

Der ältere `collect_duesseldorf_data.py` bleibt ein optionaler Direktabruf für spätere Aktualisierungen. Er ist für den reproduzierbaren Stand 0.10 nicht nötig. Die Cloud-Sperre der direkten Originalserver bleibt damit eine Eigenschaft dieser Entwicklungsumgebung und blockiert diese Version nicht mehr.

## Gemeinsame Funktionen und Bestandsschutz

`bootstrap.js` zeigt zuerst die Stadtauswahl. `?region=taipei` und `?region=duesseldorf` laden jeweils nur das benötigte regionale Paket. `region-ui.js` lokalisiert die Oberfläche; `app.js` und `street-map.js` bleiben gemeinsame Lern- und Kartenlogik. Unbekannte Regionen führen zur Stadtauswahl.

Die bisherigen Schlüssel `taipei-kennen.settings.v1` und `taipei-kennen.progress.v1` bleiben erhalten. Düsseldorf verwendet eigene Schlüssel `duesseldorf-kennen.settings.v1` und `duesseldorf-kennen.progress.v1`. Sicherungen enthalten die Region; alte Sicherungen ohne Region bleiben Taipei-Sicherungen. Ein Import in die falsche Region wird abgewiesen.

Beim Upgrade des Düsseldorfer Zwischenstands mit Datenversion 1 auf Version 2 werden die erstmals verfügbaren Bahn- und Flussebenen initial eingeblendet und Flüsse vorausgewählt. Bisherige Quizantworten bleiben erhalten. Danach werden die eigenen Anzeigeeinstellungen wieder unverändert respektiert.

Eine bewusste Stadtauswahl öffnet zuerst die Themen. Neuladen innerhalb einer Region kann die gespeicherte Ansicht wiederherstellen. Die Gebietsauswahl bleibt während laufender Runden gesperrt. Die Offline-Einzeldatei enthält beide Regionen und sämtliche Skripte; im Spiel erfolgen keine externen Datenabrufe.
