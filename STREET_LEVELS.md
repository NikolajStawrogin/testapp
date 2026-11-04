# Straßen in Leveln lernen · 0.12

## Bedienung

Stadt → Straßen → Lerngebiet wählen. Standard ist „Level · jeweils 10 neue Straßen“. Level 1 enthält die zehn längsten Straßen des gewählten Gebiets nach der unten beschriebenen Schätzung, Level 2 die nächsten zehn und so weiter. Das letzte Level kann weniger als zehn Straßen enthalten. Die Auswahl gilt für Entdecken, Lernkarten und Quiz.

Jeder Düsseldorfer Stadtteil, jeder Bezirk in Taipei/New Taipei, jede ganze Stadt und jede eigene Kombination von Gebieten hat eine eigene gespeicherte Level-Position. Die beiden Lernregionen behalten getrennte Speicher. Beispiele aus dem vorhandenen Datenbestand: Eller hat 125 Straßen und 13 Level, Wersten 113 Straßen und 12 Level, ganz Düsseldorf 2.891 Straßen und 290 Level.

Nach einer Runde startet „Nächstes Level starten“ das nächste Level im gleichen Lernmodus. Vorherige und spätere Level können auch direkt gewählt werden. Es gibt keine vorgeschriebene Mindestpunktzahl und keine Sperre. Ein Wechsel ersetzt normalerweise die zehn aktuellen Straßen. „Frühere Level mitüben“ nimmt die bereits durchlaufenen Level zusätzlich auf: Level 2 enthält dann bis zu 20 Straßen, Level 3 bis zu 30. Die Quiz-Rundenlänge (5, 10 oder alle) bleibt separat wählbar.

Die Anzeige „schon richtig gefunden“ zählt Straßen mit mindestens einer richtigen Quizantwort. Lernkarten zählen nicht als richtige Antworten. Ergebnisse zu derselben Straße gelten auch in anderen Gebiets-Auswahlen derselben Region. Die Kartenansicht hebt die aktuellen Lernstraßen gegenüber dem übrigen Straßennetz hervor. Während einer Level-Quizfrage sind Straßennamen bis zur Auflösung verborgen, damit die gesuchte Straße nicht durch fehlende Beschriftung auffällt.

„Freie Auswahl“ bietet weiterhin Suche, Einzelwahl und die vorhandenen Klassen-/Unterteilungsfilter. Diese Filter verändern die feste Level-Einteilung nicht. Level verwenden ganze benannte Straßen, keine einzelnen Sections. Bei Taipei gelten im reinen Englisch-Modus nur Straßen mit belegtem englischen Namen; dadurch kann dessen Einteilung abweichen. Deutsch beziehungsweise traditionelle Zeichen enthalten auch Straßen ohne englischen Namen.

Level-Positionen bleiben nach Neuladen erhalten und werden mit dem Lernstand exportiert/importiert. Alte Sicherungen ohne Level-Daten bleiben lesbar und überschreiben keine Level-Positionen. „Lernfortschritt löschen“ setzt auch die Level-Positionen der aktuellen Region zurück; andere Regionen bleiben erhalten.

## Was bedeutet „größte Straße“?

Die Reihenfolge verwendet die geschätzte Länge des Hauptverlaufs **innerhalb des gewählten Gebiets**. Eine lange Straße quer durch Düsseldorf kann in Eller nur ein kurzes Stück besitzen und dort später erscheinen. Bei mehreren individuell gewählten Stadtteilen werden deren Teil-Schätzungen addiert. Ganze Städte beziehungsweise die ganze Lernregion besitzen gesonderte Längenwerte. Gleichstände werden anhand der stabilen Straßenkennung aufgelöst.

Grundlage sind die bereits vorhandenen lokalen Liniengeometrien, keine neue kostenpflichtige API. Straßenbreite, Verkehrsstärke und Bedeutung sind daraus nicht verlässlich bekannt. Die Werte dienen der Lernreihenfolge und sind keine amtlichen Längen oder Zusage einer exakten Rangliste. Quellenalter, fehlende Wege und Geometriefehler des bestehenden Datenbestands gelten weiterhin.

## Reproduzierbare Aufbereitung

`tools/build_street_levels.py` erzeugt `data/levels-duesseldorf.js` und `data/levels-taipei.js` offline mit Python und Shapely 2.1.2. Die Dateien enthalten SHA-256 der Eingabedaten, gerundete Meter-Schätzungen je Straße und Gebiet sowie die Kennung der Berechnungsmethode. Zur Laufzeit lädt die App nur die Metadaten ihrer Region; Level-Wechsel benötigen keine Netzwerkabfrage oder Geometrieanalyse im Browser.

Die Berechnung projiziert Koordinaten näherungsweise in lokale Meter, schneidet die Linien an den Gebietsgrenzen und schätzt den längsten verbundenen Hauptverlauf. Doppelte Segmente werden vereinigt. Breite geschlossene Ringstraßen werden als Umfang berücksichtigt; nahe parallele Fahrbahnen werden über eine gepufferte Korridor-Schätzung normalisiert, damit ihre Längen nicht einfach doppelt zählen. Verzweigungen, getrennte Straßenteile und dichte Kurven bleiben Näherungen. Die Originalgeometrie wird nicht verändert.

Die abgeleiteten Metadaten unterliegen denselben Quellen- und Lizenzhinweisen wie die zugrunde liegenden Straßen; siehe THIRD_PARTY_NOTICES.md und REGIONEN.md.
