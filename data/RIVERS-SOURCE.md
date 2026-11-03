# Flussflächen: Herkunft und Bearbeitung

Enthalten sind die vier großen Flüsse 淡水河 (Tamsui River), 基隆河 (Keelung River), 新店溪 (Xindian River) und 大漢溪 (Dahan River). Es handelt sich um Flussflächen aus einem vereinfachten Referenzbestand, nicht um Live-Wasserstände oder neu bestätigte Ufergrenzen.

## Nachvollziehbare Quelle

- Ursprünglicher Datenanbieter: 經濟部水利署 / Taiwan Water Resources Agency (WRA).
- Primärdatensatz: `RIVERPOLY`, [WRA GIS](https://gic.wra.gov.tw/Gis/gic/API/Google/Index.aspx).
- Im veröffentlichten Notebook dokumentierter Download: `https://gic.wra.gov.tw/Gis/gic/API/Google/DownLoad.aspx?fname=RIVERPOLY&filetype=SHP`.
- Verwendete Kopie: [hankc0215/ARIA, interactive_risk_map_light.html](https://github.com/hankc0215/ARIA/blob/89dbc71b78a3c1b9cb6896f4b3d59576942685e3/interactive_risk_map_light.html).
- Feste Git-Version: `89dbc71b78a3c1b9cb6896f4b3d59576942685e3`.
- SHA-256 der vollständigen HTML-Quelldatei: `3ac4f7b7728f7aec29aa95c1cca03e73c16aa3a7dac8e5b75af237a4cadabe78`.
- Herkunftsbeleg: `ARIA.ipynb` derselben Version dokumentiert Download, Umrechnung nach WGS84 / EPSG:4326 und Vereinfachung mit Toleranz 0,0001 Grad vor dem HTML-Export. Die vollständige eingebettete Fluss-Sammlung enthält 13.262 Features mit `RIVER_NAME`, `RIVER_FROM`, `RIVER_CODE` und `RIVER_TYPE`.
- Abruf und Prüfung der Kopie: 3. November 2026. Der heutige Primärbestand wurde nicht direkt verifiziert; aus dem Abrufdatum folgt kein aktueller amtlicher Datenstand.

## Lokaler Auszug

`river-areas-source.geojson` enthält unveränderte GeoJSON-Features der vier ausgewählten Namen: 34 für Tamsui, 133 für Keelung, 51 für Xindian und 111 für Dahan. Es wurde kein fremder Anwendungscode übernommen.

`tools/build_river_data.py` prüft die Prüfsumme der vollständigen HTML-Kopie, extrahiert nach `RIVER_NAME`, vereinigt zusammengehörige Flächen, repariert Geometrien, schneidet sie auf die dargestellten Grenzen von Taipei City und New Taipei City zu und rundet Koordinaten auf sechs Nachkommastellen. Innenringe bleiben erhalten. Geometrien werden nicht zu erfundenen Verbindungen ergänzt. Interne IDs, Orientierungstexte und in den Flächen liegende Beschriftungspunkte werden ergänzt. `rivers.js` enthält nur diesen lokalen Auszug und die Quellenmetadaten.

Die Stadtzugehörigkeit wird aus der Schnittfläche mit den Bezirksgeometrien berechnet. Dahan ist im New-Taipei-Gebiet spielbar; Tamsui, Keelung und Xindian in beiden Stadtgebieten. Die Flüsse können außerhalb des Kartenausschnitts weiterlaufen. Die Umrisse der beiden Referenzbestände sind unterschiedlich alt und können geringfügig voneinander abweichen.

Traditionelle chinesische Namen werden unverändert aus `RIVER_NAME` übernommen. Die englischen gebräuchlichen Namen wurden als Metadaten ergänzt; ein aktueller Abgleich mit einer amtlichen englischen Namensliste steht aus.

## Rechte und Quellenangabe

Die Flussdaten stammen vom oben genannten staatlichen Anbieter. Die sichtbare Kartenquellenangabe nennt die Water Resources Agency, auch im Quiz. Die GitHub-Kopie erklärt keine gesonderte Datenlizenz. Aus ihrer öffentlichen Verfügbarkeit wird keine CC0- oder MIT-Lizenz für die Flussdaten abgeleitet. Die aktuellen Bedingungen des Primäranbieters, einschließlich der Anwendbarkeit der [taiwanischen Government Data Open License](https://data.gov.tw/license), sind noch nicht abschließend verifiziert. Inzwischen hat der Nutzer eine öffentliche GitHub-Pages-Bereitstellung beauftragt; die Quellenangaben und diese Nachweisgrenzen werden dabei weiter ausgewiesen.

Zum erneuten Erzeugen der lokalen Daten wird für die Entwicklung `shapely` benötigt. Die fertige Browser-App benötigt weder dieses Paket noch einen Online-Abruf.
