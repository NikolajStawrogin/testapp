# Datenquellen und Rechtehinweise

## Bezirksgeometrien

- Projekt: [g0v/twgeojson](https://github.com/g0v/twgeojson)
- Autor laut README: Chia-liang Kao
- Bereitstellung laut Projekt: [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
- [Lizenzangabe im README an der verwendeten Git-Version](https://github.com/g0v/twgeojson/blob/85212c5cff73b706730e624024120b134c15f861/README.md)
- [Verwendete Geometriedatei](https://github.com/g0v/twgeojson/blob/85212c5cff73b706730e624024120b134c15f861/json/twTown1982.geo.json)
- Git-Version: `85212c5cff73b706730e624024120b134c15f861`

Für `data/districts.js` wurden die zwölf Features mit `COUNTYNAME=台北市` und die 29 Features mit `COUNTYNAME=新北市` entnommen. Polygon- und MultiPolygon-Flächen bleiben erhalten; die ursprünglichen zwölf internen IDs bleiben für bestehende Lernstände unverändert. Koordinaten wurden auf sechs Nachkommastellen gerundet. Interne IDs, bilinguale Namen, Orientierungstexte und innerhalb der Flächen berechnete Beschriftungspunkte wurden ergänzt. Die Quelldatei wurde gegen die feste Git-Version abgeglichen; ihr SHA-256 steht in den Metadaten der lokalen Datei.

Es handelt sich um einen vereinfachten Referenzbestand, nicht um einen neu bestätigten amtlichen Grenzstand.

## Bezirksnamen

Die 41 traditionellen chinesischen Namen und englischen Schreibweisen wurden nach der untersuchten Kopie des Chunghwa-Post-Bezirksverzeichnisses, Ausgabe 109/06, verwendet. Quelle und Grenzen der Verifikation stehen in [OFFIZIELLE_NAMEN.md](OFFIZIELLE_NAMEN.md).

Es werden weder die vollständigen Postverzeichnisse noch Bibliotheken privater Adressübersetzer mitgeliefert. Die Herkunfts- und Rechteprüfung eines vollständigen künftigen Straßennamenbestands ist noch offen.

## Metro-Geometrien

- © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- [Quellenangabe OpenStreetMap](https://www.openstreetmap.org/copyright)
- Bereitgestellter Auszug: [davidyen1124/mrt-app, taipei_lines.geo.json](https://github.com/davidyen1124/mrt-app/blob/32a31120995022944ef4c59cf0484ce15b22bccc/data/taipei_lines.geo.json)
- Feste Git-Version: `32a31120995022944ef4c59cf0484ce15b22bccc`
- Auszugsdatum laut Datei: 27. September 2026
- SHA-256 der Quelldatei: `8a6a247284c5db5e91369db341e22d54798f9e1f826a8ac328b80ce9ae94da93`

`data/metro.js` enthält die ursprünglichen neun OSM-Verläufe einschließlich Y und GA sowie ergänzende Geometrien für A, V, K und LB. Insgesamt werden 12 Linienkennungen und 13 Routen dargestellt. Die ausgewählten Streckenkoordinaten wurden aus den Ausgangsdaten unverändert übernommen. Für die Zusatzlinien wurden eindeutige Way-Geometrien aus OSM-Routenrelationen entnommen; inaktive und Nicht-Strecken-Mitglieder wurden ausgeschlossen. Getrennte Teilstücke werden nicht durch erfundene Verbindungen verbunden. Linienbezeichnungen und Farben wurden als zusätzliche Metadaten ergänzt. Die Anzeige verwendet dieselbe Projektion wie die Bezirksflächen und wird an den gemeinsamen Grenzen von Taipei City und New Taipei City abgeschnitten.

Die Zusatzlinien stammen aus [rareone0602/taipei-mrt-minecraft](https://github.com/rareone0602/taipei-mrt-minecraft/tree/aaaa1d71ce30ebb4371c13ed83f6e199a2e8cfcd/data/lines), dessen `LICENSE-DATA` die Dateien ausdrücklich als ODbL-Daten ausweist. Die Ausgangsdateien A, V, K und LB liegen unverändert in `data/metro-extra-source/`; feste Versionen, OSM-Zeitstempel und Prüfsummen stehen in den Metadaten von `data/metro.js`. Die Datenstände reichen von Juni bis September 2026. Die Flughafen-MRT erhält zur Lesbarkeit einen dunkleren violetten Darstellungston.

Der vollständige ursprüngliche OSM-Auszug liegt in `data/metro-routes-source.geojson`, die Lizenz- und Bearbeitungshinweise in [data/METRO-LICENSE.md](data/METRO-LICENSE.md). Die geografische Metro-Datenbank einschließlich der Auswahl wird unter ODbL 1.0 bereitgestellt. Die Bezirksflächen bleiben als separates CC0-Datenset dokumentiert. Es wurde kein Anwendungscode des Ausgangsprojekts übernommen.

Die Quellenangabe ist bei aktivierter Ebene im Kartenfuß sichtbar, auch im mobilen Quiz. In „Quellen & Datenstand“ sind Herkunft und Datenstand zusätzlich beschrieben.

## Flussflächen

Die vier Flüsse stammen aus dem `RIVERPOLY`-Datensatz der Taiwan Water Resources Agency (WRA), übernommen aus einem fest versionierten, veröffentlichten GIS-Auszug. Namen wurden anhand von `RIVER_NAME` ausgewählt; 329 ursprüngliche GeoJSON-Features sind in `data/river-areas-source.geojson` enthalten. `data/rivers.js` enthält den vereinigten, auf die beiden Städte begrenzten Auszug. Es wurde kein Anwendungscode des Quellprojekts übernommen. Die Flussdaten sind separat von den CC0-Bezirksflächen und den ODbL-Metro-Daten dokumentiert. Quellenlinks, Prüfsummen, Bearbeitungsschritte und der noch ausstehende Abgleich der aktuellen Nutzungsbedingungen beim Primäranbieter stehen in [data/RIVERS-SOURCE.md](data/RIVERS-SOURCE.md).

## Straßen-Geometrien und Namen

© OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). `data/streets.js` und die in `data/street-sources.zip` archivierten OSM-Auszüge enthalten eine aus OSM abgeleitete Straßendatenbank, die einschließlich der Auswahl und Bearbeitung unter ODbL 1.0 angeboten wird. Quellen sind die festen Versionen `c3d387948e48adc38440062b33a19e1aca1b8b36` von `typebrook/mapstew` (565 Kacheln, Version Dezember 2021) und `96af2cbce0b40dd6120d2719ec7ee3b6027d94f3` von `jpchen/taipei-3d-render` (Innenstadt-Auszug, September 2026). Es wurde kein Anwendungscode dieser Projekte übernommen.

Englische Namensmetadaten verwenden die separat dokumentierten Postreferenz-Kopien der festen Version `2a5923e5de751e24586901082a7df80653e7a96e` von `sean1093/menpai`. Ihre Primärquellen-, Aktualitäts- und Rechteprüfung bleibt entsprechend `OFFIZIELLE_NAMEN.md` offen; eine OSM- oder Softwarelizenz wird nicht pauschal auf amtliche Namensreferenzen übertragen. Datenbearbeitung, Quellenhashes, Namensherkunft, fehlende englische Namen und die Namens-/Geometrie-Abdeckung je Bezirk sind in [data/STREETS-SOURCE.md](data/STREETS-SOURCE.md), `data/street-source-manifest.json` und `data/street-coverage.json` dokumentiert. Die Kartenquellenangabe ist im Straßenmodus sichtbar.

## Weitere Bestandteile

Die App lädt keine externen Schriftdateien, Kartenkacheln oder JavaScript-Bibliotheken. Die Icons bestehen aus im Projekt enthaltenen SVG-Linienzeichnungen. Python stellt nur den lokalen Dateiserver über seine Standardbibliothek bereit. Playwright ist ausschließlich ein Entwicklungswerkzeug für die Tests und wird nicht mit dem Nutzerpaket installiert.

## Düsseldorf · regionale Erweiterung

Stadtteilgrenzen und Straßen stammen aus OpenStreetMap-Auszügen in den Projekten codeforgermany/click_that_hood und ckrey/stressmap. © OpenStreetMap contributors, Open Database License 1.0: https://www.openstreetmap.org/copyright und https://opendatacommons.org/licenses/odbl/1-0/ . Die abgeleitete Düsseldorfer Geodatenbank wird unter ODbL 1.0 bereitgestellt. Originalkopien, festgehaltene Versionen und SHA-256 stehen unter data/duesseldorf. Stadtbezirke werden aus den dokumentierten Stadtteilzuordnungen abgeleitet. Diese historischen Daten sind kein aktuell amtlich geprüftes Straßenverzeichnis. Flüsse stammen zusätzlich aus dem fest versionierten OSM-Auszug von 3ddruck12/flowtrail-pegel (27.05.2026), ebenfalls ODbL 1.0. Blaue Flächen sind abgeleitete Puffer um diese Mittellinien. Bahnlinien verwenden VRR-GTFS-Haltestellen und Haltefolgen aus n3koBomb/linienblick, Version 25.08.2026; Quelle und Namensnennung: Verkehrsverbund Rhein-Ruhr (VRR). Der verlinkte Verkehrsverbund-Katalog nennt CC BY ohne Versionsangabe; eine bestimmte Lizenzversion wird nicht behauptet. Die Geometrie ist als schematische Verbindung zwischen Haltestellen gekennzeichnet. Die Bahn-Daten werden nicht pauschal als OSM/ODbL ausgegeben. Beide Datenquellen und Hashes sind in layers-source-manifest.json dokumentiert. Einzelheiten: REGIONEN.md.
