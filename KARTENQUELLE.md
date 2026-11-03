# Kartenquelle: Vergleich und Entscheidungsvorlage

Stand: 3. November 2026. Status: lokale Bezirks-, Fluss- und Straßenkarte für beide Städte in Version 0.7 umgesetzt. Der heutige amtliche Vollständigkeitsnachweis bleibt offen.
Nach Umgebungswechsel wiederhergestellt und um neu gelesene offizielle Quellen ergänzt.

## Umgesetzte Darstellung und verbleibende Datenprüfung

Version 0.7 stellt lokale OSM-Straßenobjekte und Bezirks-/Flussflächen gemeinsam als SVG dar. Straßen werden abhängig vom sichtbaren Ausschnitt und Zoom dargestellt, volle Einheiten beim Überfahren hervorgehoben und für Antworten geografisch getroffen. Das benötigt keine Karten-API, externen Kacheln oder Hostingkosten. MapLibre bleibt eine spätere Darstellungsoption bei weiterem Umfang. Amtliche Namensaktualität und Bezirksgrenzen benötigen weiterhin Quellenprüfung.

Die Bezirkskarte verwendet lokale CC0-Geometrien aus `g0v/twgeojson`. Dieser vereinfachte Referenzbestand ist nicht als aktueller amtlicher Grenzstand bestätigt; Quelle, feste Git-Version und Änderungen stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Der Straßenkatalog unterscheidet Straßen, Sections, Lanes und Alleys als eigene auswählbare Einheiten. Namensherkunft und Zugehörigkeit zu Bezirken sind dokumentiert; gleiche Namen im selben Bezirk werden ohne künstliche Geometrieverbindungen zu einer Aufgabe vereinigt. Die implementierte Darstellung und der lokale Betrieb sind überprüfbar. Der heutige amtliche Vollständigkeitsnachweis und der abschließende Rechteabgleich vor öffentlicher Veröffentlichung bleiben offen.

Die vertiefte Namensrecherche steht in [OFFIZIELLE_NAMEN.md](OFFIZIELLE_NAMEN.md). Die geprüften Postkopien liefern eindeutige Namenspaare; nummerierte Gassen werden aus belegten Basisnamen und Adresszusätzen gebildet. Weitere englische Namen stammen aus OSM oder werden ausdrücklich als fehlend behandelt. Für die Geometrien sind ein flächendeckender OSM-Kachelstand von 2021 und ein Innenstadt-Auszug von 2026 fest versioniert und lokal archiviert. Die Zuordnung von 22.039 Einheiten zu allen 41 Bezirken, Namensherkunft, Bearbeitung und Grenzen sind in [data/STREETS-SOURCE.md](data/STREETS-SOURCE.md) und [data/street-coverage.json](data/street-coverage.json) dokumentiert.

## Verbindliche Vorgaben: lokal auf dem eigenen Rechner, keine Hostinggebühren

Der Nutzer akzeptiert keine Hostingkosten. Damit entfallen bezahltes Kartenhosting, ein gemieteter Server und ein notwendiger kostenpflichtiger Hostingtarif als Voraussetzungen des vorgeschlagenen Betriebsmodells.

Lokale Bereitstellung ist für die persönliche erste Version bestätigt. Dafür vorgesehener technischer Ansatz:

- App, benötigte Kartendarstellung und ein vorbereiteter Datensatz für beide Städte werden lokal auf einem vorhandenen Gerät bereitgestellt.
- Die Bedienung bleibt im Browser. Ein kleiner lokaler Webserver auf dem eigenen Rechner kann dafür erforderlich sein; ein eigener Mietserver ist dafür nicht nötig.
- MapLibre, Stil, Schriftdateien und sämtliche für den vereinbarten Kartenausschnitt benötigten Daten werden mitgeliefert. Für Kartenabfragen im laufenden Betrieb wird bei dieser Variante keine externe Bezahl-API eingeplant.
- Die lokale Karte unterstützt grundlegende Touch-Gesten einschließlich Zweifinger-Zoom. Eigenständiger Smartphone-Zugang und weitere Smartphone-Anpassungen bleiben spätere Erweiterungen.
- Öffentliche Bereitstellung und Auswahl eines Hostinganbieters entfallen für die erste Version. Bei einer späteren Veröffentlichung wären kostenlose statische Angebote gesondert zu prüfen. Ein Freikontingent mit möglicher automatischer Nachberechnung erfüllt die Kostenvorgabe nicht.

Die Entscheidung für lokale Bereitstellung ist bestätigt, die genaue technische Umsetzung bleibt eine Planungsempfehlung. Datenumfang, Geräteleistung, rechtmäßig beziehbare Ausgangsdaten und ein praktikabler lokaler Start müssen noch geprüft werden. Vollständige Offline-Fähigkeit ist damit noch nicht verlangt oder nachgewiesen. Der vorhandene Rechner und gegebenenfalls Internet für die anfängliche Datenbeschaffung werden vorausgesetzt; keine zusätzlichen Hostinggebühren sind einzuplanen.

## Drei getrennte Bausteine

1. Kartenanzeige: Zoomen, Orientierung und selbst steuerbare Beschriftungen.
2. Straßengeometrien und Bezirksflächen: eindeutige Objekte für Auswahl, Hervorhebung und Lösung. Bezirksauswahl und Kartenzoom unterstützen Maus und Touch; die Touch-Auswahl von Straßen bleibt noch zu planen.
3. Quizkatalog: traditionelle chinesische Namen, offizielle englische Schreibweisen, Kategorien, Gebietszuordnung und stabile Identitäten.

MapLibre ist Darstellungssoftware, OSM eine Datenquelle. Die Kombination garantiert keine amtlichen englischen Namen. Vektorkacheln beziehungsweise andere geeignete lokale Geodaten, Stil, Schriftdateien und Quizdaten müssen für die geplante lokale Darstellung bereitgestellt werden; ein externer Kartenhostingdienst ist dafür nicht zwingend nötig.

## Funktionsvergleich

| Kriterium | Google Maps | MapLibre mit eigenen OSM-basierten Daten |
| --- | --- | --- |
| Zoombare Karte | Möglich | Möglich |
| Eigene Objekte mit Mausereignissen | Offizielles Beispiel für GeoJSON-Datenebene und `mouseover` gelesen | Offizielle APIs für Objektabfrage, Feature-Zustand und Filter gelesen |
| Beliebige dargestellte Straße als Quizobjekt | Keine Zusage: eigene Datenebene ist kein Zugriff auf Googles zugrunde liegenden Straßenkatalog | Eigene Geometrien und stabile IDs ermöglichen die gewünschte Auswahl; Datenaufbereitung bleibt erforderlich |
| Beschriftungen steuern | Offizielles Beispiel belegt Styling nach Objektklassen; kein Nachweis selektiver Unterdrückung eines einzelnen Straßennamens | Mit kontrolliertem Stil, getrennten Beschriftungsebenen und passendem Quizdatensatz planbar |
| Nur den gesuchten Namen verstecken | Nicht ohne zusätzlichen Nachweis zusagen | Planbar, aber nicht mit beliebigen fertigen Tiles garantiert; Namens- und Quiz-IDs müssen zusammenpassen |
| Sections, Lanes und Alleys | Kartenanzeige allein belegt weder exportierbaren Katalog noch Nutzungsrecht | Grundsätzlich aus geeigneten Daten erschließbar; Taipei-Abdeckung ungeprüft |
| Amtliche englische Schreibweise | Nicht aus einer sichtbaren Beschriftung ableiten | `name:en` allein ist ebenfalls kein Amtlichkeitsnachweis |
| Kosten | Gebührenfreiheit für unseren Betrieb nicht belegt; daher keine empfohlene Grundlage unter der Kostenvorgabe | Keine MapLibre-Softwarelizenzgebühr; bestätigte lokale Bereitstellung ohne zusätzliches bezahltes Hosting, Datenaufbereitung noch zu prüfen |
| Später Google Street View | Eigenständig auf API, Kosten und Bedingungen prüfen | Zulässigkeit einer Verbindung mit dieser Kartenwahl nicht voraussetzen |

## Verifizierte technische Grundlage

Offizielle MapLibre-Quellen enthalten `queryRenderedFeatures`, `setFeatureState`, `setLayoutProperty` und `setFilter`. Sie bilden die Grundlage für auswählbare Straßen und kontrollierte Darstellung. Das ist ein Quellennachweis, kein ausgeführter Prototyp.

Googles offizielle Beispiele zeigen das Einlesen eigener GeoJSON-Objekte, Ereignisse auf diesen Objekten und das Ausblenden von Objektklassen über Styling. Daraus folgt nicht, dass sämtliche Google-Straßen als einzeln abfragbare Geometrien verfügbar sind oder dass sich nur die aktuell gesuchte Straßenbeschriftung entfernen lässt.

OpenMapTiles trennt `transportation` und `transportation_name`. Die Namensebene enthält nur geeignete benannte Linien und kann gleichnamige Segmente für bessere Beschriftung zusammenfassen. Das Feld `name_en` kann laut Schema bei fehlendem englischem Namen auf `name` zurückfallen. Deshalb ist eine vorhandene Beschriftung weder Vollständigkeitsnachweis noch Beleg eines englischen amtlichen Namens. Ein eigener Quizkatalog bleibt nötig.

## Verifizierte Lizenz- und Betriebsgrundlagen

- MapLibre GL JS wird unter BSD-3-Clause bereitgestellt; die im Projekt dokumentierten Hinweise und Drittkomponentenlizenzen sind zu berücksichtigen.
- Die offizielle OSM-Copyright-Seite nennt die ODbL für die Daten. Namensnennung ist erforderlich. Bei Weitergabe beziehungsweise öffentlicher Nutzung abgeleiteter Datenbanken sind die konkreten ODbL-Pflichten zu prüfen; die gesamte Anwendung wird dadurch nicht pauschal einer gleichen Lizenz unterstellt.
- Öffentliche OSM-Raster- und Vektorkartenserver haben begrenzte Kapazität, keine Verfügbarkeitsgarantie und eigene verbindliche Nutzungsregeln. Die Richtlinien verlangen unter anderem sichtbare Namensnennung und regelkonformes Caching; Massendownloads beziehungsweise Vorababrufe sind untersagt. Eigene Stadtdatenauszüge sind deshalb über dafür erlaubte Datenquellen zu beschaffen, nicht durch Sammeln öffentlicher Kartenkacheln.
- Kartenanbieter und Datenquelle haben getrennte Bedingungen. OSM-Daten bedeuten nicht automatisch kostenloses oder unbegrenzt nutzbares Kartenhosting.

## Erfolgreich gelesene offizielle Quellen

Abruf am 3. November 2026 über die offiziellen GitHub-Projekte, die in der bestehenden Netzwerkfreigabe erreichbar sind:

- [MapLibre-Karten-API](https://github.com/maplibre/maplibre-gl-js/blob/main/src/ui/map.ts)
- [MapLibre-Lizenz](https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt)
- [Google: Klassen ausblenden](https://github.com/googlemaps/js-samples/blob/main/samples/hiding-features/index.ts)
- [Google: eigene Daten und Mausereignisse](https://github.com/googlemaps/js-samples/blob/main/samples/layer-data-event/index.ts)
- [OpenMapTiles: Straßen](https://github.com/openmaptiles/openmaptiles/blob/master/layers/transportation/transportation.yaml)
- [OpenMapTiles: Straßennamen](https://github.com/openmaptiles/openmaptiles/blob/master/layers/transportation_name/transportation_name.yaml)
- [OSM: offizieller Copyright-Seitentext](https://github.com/openstreetmap/openstreetmap-website/blob/master/config/locales/en.yml), Abschnitt `site.copyright`
- [OSM: Richtlinie für Rasterkacheln](https://github.com/openstreetmap/owg-website/blob/main/policies/tiles.md)
- [OSM: Richtlinie für Vektorkacheln](https://github.com/openstreetmap/owg-website/blob/main/policies/vector.md)

## Noch ungeprüfte Quellen

Die folgenden Direktabrufe waren auch in der neuen Umgebung mit `403 Forbidden` des bereitgestellten Proxys blockiert. Keine aktuellen Preise, Kontingente oder Google-Vertragsfreigaben werden daraus behauptet:

- Google-Dokumentation: https://developers.google.com/maps/documentation/javascript/style-reference
- Google-Datenebenen: https://developers.google.com/maps/documentation/javascript/dds-datasets/overview
- Google-Preise: https://developers.google.com/maps/billing-and-pricing/pricing
- Google-Bedingungen: https://cloud.google.com/maps-platform/terms
- MapLibre-Beispiel: https://maplibre.org/maplibre-gl-js/docs/examples/create-a-hover-effect/
- OSM-Copyright-Seite: https://www.openstreetmap.org/copyright
- Taiwan-Tagging: https://wiki.openstreetmap.org/wiki/Taiwan/Tagging
- Taiwan-Auszug: https://download.geofabrik.de/asia/taiwan.html
- Amtliche Daten: https://data.taipei/

Für OSM-Serverrichtlinien und Copyright-Seitentext konnten stattdessen die offiziellen GitHub-Quellen gelesen werden; deren Inhalte sind oben getrennt als verifiziert aufgeführt.

## Vor endgültiger Kartenwahl nachzuweisen

1. Reale Taipei-Beispiele für große Straße, Section, kleine Straße, Lane und Alley: Geometrie, Namen und eindeutige Quizidentität.
2. Amtliche englische und chinesische Namen aller verwendeten Aufgaben sowie Flächen aller 41 Bezirke beider Städte: konkrete Quelle, Aktualität und Lizenz.
3. Abdeckungsbericht: fehlende Namen oder Geometrien transparent machen, keine ungeprüfte Vollständigkeitszusage.
4. Zusammenhängende Auswahl der richtigen Straßeneinheit ohne gleichnamige andere Straßen; Regeln für Bezirksgrenzen, Kreuzungen und übereinanderliegende Straßen.
5. Beschriftungskonzept ohne verratene Lösung, auch bei aktivierten Orientierungshilfen.
6. Zuverlässige Mausauswahl und grundlegende Touch-Bedienung der Bezirkskarte. Der Kartenzoom muss mit zwei Fingern funktionieren und darf keine Quizantwort auslösen. Touch-Auswahl und Hervorhebung von Straßen sind gesondert zu prüfen.
7. Lokaler Start und lokale Bereitstellung ohne Hostinggebühren samt zulässiger gemeinsamer Datennutzung, Namensnennung, Datengröße und Ladeverhalten. Kein öffentlicher Server oder Smartphone-Zugang nötig; keine automatische Nachberechnung.

## Stand der Umgebung

### Umgesetzte Metro-Orientierungsebene

Der Bezirksprototyp 0.4 enthält lokale OSM-Metrogeometrien aus dokumentierten Auszügen von Juni bis September 2026. BR, R, G, O, BL und Y, Flughafen-MRT A, Danhai V, Ankeng K, Sanying LB sowie die Abzweige RA und GA werden in derselben Projektion über den 41 Bezirksflächen dargestellt und an den gemeinsamen Grenzen beider Städte abgeschnitten. Die Ebene ist ohne externe Karten-API ein-/ausblendbar und funktioniert mit Touch-Zoom.

Die Hauptquelle ist an Git-Version `32a31120995022944ef4c59cf0484ce15b22bccc` des Projekts `davidyen1124/mrt-app` gebunden; die zusätzlichen Linien A, V, K und LB stammen aus ODbL-Daten der Git-Version `aaaa1d71ce30ebb4371c13ed83f6e199a2e8cfcd` von `rareone0602/taipei-mrt-minecraft`. Es wurden ausschließlich OSM-Geodaten, keine Anwendungscodebestandteile übernommen. Originaldaten, unveränderte ausgewählte Geometrien und ODbL-Hinweis sind lokal mitgeliefert; Quellen und Änderungen stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

### Netzwerk für weitere Quellenprüfung

Die Einstellung „Vollzugriff“ hat laut anschließender Prüfung die separaten Netzwerkregeln der Cloud-Umgebung nicht geändert. Die aktive Netzwerkrichtlinie bleibt eingeschränkt ohne zusätzliche benutzerdefinierte Domains.

Die nötigen Dokumentationsdomains sind erneut im aktuellen Konfigurationsentwurf gespeichert, aber nicht nachweislich angewendet oder veröffentlicht. Aus dem verfügbaren Werkzeugumfang kann die Veröffentlichung nicht selbst ausgelöst werden. Ein Neustart allein ist kein Nachweis, dass der Entwurf aktiv wurde. Es werden keine weiteren Änderungen am Chatmenü als Lösung zugesagt.

Die Prüfung amtlicher Taipei-Daten und ihrer Lizenz bleibt notwendig. Google-Preise sind für den vorgeschlagenen lokalen Betrieb ohne Google-Dienste kein erforderlicher Prüfschritt mehr; ihre Unkenntnis blockiert diesen Vorschlag nicht. Die bereits erlaubten offiziellen GitHub-Quellen liefern technische und betriebliche Teilnachweise. Bis Datenabdeckung und gebührenfreie Bereitstellung nachgewiesen sind, bleibt die Empfehlung vorläufig.


## Düsseldorf · verfügbare Quellen seit 0.10

Die regionale App enthält nun sechs aus tatsächlichen OSM-Gewässer-Mittellinien abgeleitete Flüsse und 26 schematische Bahnlinien aus belegten VRR-GTFS-Haltestellenfolgen. Die Gewässerquelle ist ein fest versioniertes Archiv von 3ddruck12/flowtrail-pegel (27.05.2026); die Verkehrsquelle ein VRR-Auszug aus n3koBomb/linienblick (25.08.2026). Schienenverläufe werden ausdrücklich als Haltestellenverbindungen gekennzeichnet und nicht als exakte Gleisgeometrien ausgegeben. Die vier Bahnarten sind separat schaltbar. Quellenkopien, Versionsreferenzen und Prüfsummen werden lokal mitgeliefert, sodass die Version ohne externe Karten-API, Cloud-Freigabe oder bezahlten Dienst funktioniert. Einzelheiten und Nutzungsrechte: REGIONEN.md und THIRD_PARTY_NOTICES.md.
