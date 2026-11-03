# Straßen: Datenquellen, Abdeckung und Aufgabenidentität

## Umfang

22.039 benannte Straßeneinheiten: 8.382 in Taipei City und 13.657 in New Taipei City. Alle 41 Verwaltungsbezirke besitzen Einträge. Enthalten sind 3.757 Einheiten ohne nummerierten Namenszusatz, 615 Sections, 12.055 Lanes und 5.612 Alleys. Die 831 Hauptstraßen-, 960 Verbindungsstraßen- und 20.248 Nebenstraßeneinheiten werden getrennt nach Straßenklasse und Namensunterteilung gefiltert. Die Anzahl meint unterscheidbare lokale Aufgaben; sie ist keine amtliche Zählung eindeutiger Straßennamen.

`street-coverage.json` dokumentiert die Zahlen je Bezirk und die Namensherkunft. Die Abdeckung aller Bezirke ist belegt; eine lückenlose oder aktuelle amtliche Straßenvollständigkeit ist damit nicht behauptet. OSM-Lücken, ältere Verläufe und Neubauten können fehlen.

## Geometrien

© OpenStreetMap contributors, [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Die geografische Straßendatenbank einschließlich der Auswahl und Bearbeitung wird unter ODbL 1.0 angeboten. Die CC0-Bezirksdaten bleiben separat dokumentiert.

1. Flächendeckender OSM-Kachelauszug aus [typebrook/mapstew](https://github.com/typebrook/mapstew), Zweig `gh-pages`, feste Version `c3d387948e48adc38440062b33a19e1aca1b8b36` vom 17. Dezember 2021. Das Quellprojekt dokumentiert Geofabrik/OSM als Datenherkunft. Verwendet werden die originalen `road`-Features samt OSM-Way-IDs und chinesischen Namensattributen aus 565 Kacheln auf Zoomstufe 14, die die Grenzen beider Städte schneiden.
2. Neuerer Innenstadt-Auszug aus [jpchen/taipei-3d-render](https://github.com/jpchen/taipei-3d-render/blob/96af2cbce0b40dd6120d2719ec7ee3b6027d94f3/assets/map-source.json), feste Version `96af2cbce0b40dd6120d2719ec7ee3b6027d94f3`. Die Datei nennt OSM/ODbL und den OSM-Zeitstempel 28. September 2026, 05:27:05 UTC. Ihr Abfrageausschnitt ist 25.005–25.105 N und 121.475–121.615 E. Geometrien der darin enthaltenen Straßen ersetzen alte Ways gleicher ID; nicht mehr enthaltene ältere Geometrien werden innerhalb des Ausschnitts nur für tatsächlich dort vertretene Straßenklassen entfernt. Der neuere Auszug enthält beispielsweise keine `service`-Straßen. Solche kleinen Straßen, Gassen und weitere dort nicht erfasste Klassen bleiben deshalb aus dem älteren Bestand erhalten und werden nicht als vermeintlich gelöscht verworfen.

Es wurde kein Anwendungscode der Quellen übernommen. Rohdateien und Hashes liegen vollständig in `street-sources.zip` und `street-source-manifest.json`. Die Browser-App benötigt ausschließlich `streets.js`, keine Online-Kacheln und keinen Kartenanbieter-Schlüssel.

## Namen

Die chinesischen Namen stammen aus `name:zh` beziehungsweise `name` der OSM-Quelle. Die englische Referenz sind die bereits untersuchten, fest versionierten Chunghwa-Post-Kopien von `sean1093/menpai`, Version `2a5923e5de751e24586901082a7df80653e7a96e`. Dateien und ursprüngliche URLs sind in `OFFIZIELLE_NAMEN.md` dokumentiert. Es wird kein Anwendungscode dieses Projekts verwendet.

- 3.160 englische Namen stimmen genau mit einer eindeutigen chinesisch-englischen Referenzzuordnung überein (`postal-exact`).
- 17.380 nummerierte Lanes/Alleys verwenden einen belegten Namen der übergeordneten Straße plus die numerischen Adresszusätze `Ln.` und `Aly.` (`postal-numbered`). Es werden keine Ortsnamen automatisch in Pinyin übersetzt. Diese zusammengesetzten Namen sind keine einzeln aus einem amtlichen Verzeichnis bestätigten Gasseneinträge.
- 137 weitere Namen stammen aus dem OSM-Attribut `name:en` (`osm-name-en`); eine amtliche Verifikation ist damit nicht belegt.
- Für 1.362 Einheiten ist kein englischer Name belegt (`missing`). Die App erfindet keinen Ersatznamen und behandelt diese Lücke ausdrücklich.

Die Postkopien sind reproduzierbar geprüft, aber weiterhin nicht mit der heutigen amtlichen Primärdatei abgeglichen. Der heutige Rechts- und Aktualitätsabgleich der Postreferenzen bleibt entsprechend `OFFIZIELLE_NAMEN.md` offen. Die englischen Zuordnungen dürfen nicht pauschal als aktuell amtlich verifiziert bezeichnet werden. Eine öffentliche Veröffentlichung erfordert den abschließenden Rechteabgleich dieser Referenzen; der persönliche lokale Betrieb ist der gegenwärtige Auftrag.

## Verarbeitung und Identität

`tools/collect_street_sources.py` sichert die fest versionierten öffentlichen Quellen und ihre SHA-256-Prüfsummen. `tools/build_street_data.py` prüft alle Hashes, dekodiert die Straßenmittelachsen nach WGS84, vereinigt Kachelüberlappungen pro OSM-Way und übernimmt den neueren Innenstadt-Auszug. Fußwege ohne Straßenfunktion, unbenannte Wege und allgemeine Fahrbahnbezeichnungen werden nicht als benannte Quizaufgabe ausgegeben; geeignete unbenannte Straßen dienen als Kartenhintergrund.

Verläufe werden auf die dargestellten beiden Städte zugeschnitten. Gleichnamige Straßen werden pro Stadt und räumlichem Zusammenhang zusammengefasst; räumlich entfernte Namensvetter bleiben getrennte Aufgaben. Nummerierte Sections/Lanes/Alleys werden niemals allein wegen eines gleichen übergeordneten Namens vereinigt. Ein Bezirk gilt als zugehörig, wenn sein Gebiet vom Verlauf geschnitten wird. Eine Einheit kann mehrere Bezirke berühren, die Aufgabe zeigt dann den gesamten vorhandenen Verlauf dieser Einheit innerhalb ihrer Stadt. Getrennt kartierte Teile mit gleichem Namensschlüssel innerhalb desselben Bezirks werden zu einer Aufgabe vereinigt. Dadurch kann derselbe Straßenname im selben Bezirk nicht zweimal als unterschiedlich bewertete Frage vorkommen; räumlich getrennte Namensvetter in anderen Bezirken bleiben getrennt.

Parallele Fahrbahnen beziehungsweise nahe Teilstücke werden bis etwa 70 m Nachbarschaft einer Einheit zugeordnet, ohne die Geometrien durch erfundene Verbindungen zu ergänzen. Verläufe werden auf etwa einen halben Meter vereinfacht und auf sechs Dezimalstellen gerundet. Die Karten-Toleranz der älteren Bezirksgrenzen kann an Grenzen zu kleinen Fragmenten führen. IDs werden aus Stadt, normalisiertem Namensschlüssel und räumlicher Komponente erzeugt.

## Prüfung und Reproduktion

`python -m unittest discover -s tests -p test_street_data.py -v` prüft sämtliche Quellhashes, alle 41 Bezirke, beide Städte, Sections/Lanes/Alleys, eindeutige IDs, Geometrien, Beschriftungspunkte und belegte Namensbeispiele. Für die erneute Datenerzeugung werden ausschließlich als Entwicklungswerkzeuge `shapely` und `mapbox-vector-tile` benötigt. Der fertige lokale Browserbetrieb benötigt keine Zusatzpakete.
