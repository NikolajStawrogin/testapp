# Straßenlernen und Navigation – Arbeitsauftrag

Stand: 3. November 2026. Zielversion: 0.7. Grundlage sind ANFORDERUNGEN.md und der ergänzende Auftrag zur vollständigen Straßen- und Menüerweiterung.

## Ziele und Nachweise

| Ziel | Nachweis vor Abschluss |
| --- | --- |
| Bestehende Bezirks-, Fluss- und Metrofunktionen erhalten | Vorhandene Browser-Funktionstests bestehen; alte Lernstände werden unverändert übernommen. |
| Straßen für Taipei City und New Taipei City lernen und abfragen | Reale, benannte Geometrien mit dokumentierter Quelle; Erkundung, Lernkarten, Quiz, richtige/falsche Antwort, Auswertung und Fehlerwiederholung funktionieren. |
| Gebiet und Straßenumfang verständlich wählen | Beide Städte, einzelne Stadt und Bezirksauswahl; getrennte Filter für große/kleine Straßen und für Sections/Lanes/Alleys. Leere Auswahl wird erklärt und nicht gestartet. |
| Eindeutige Namen und Aufgaben | Traditionelle Zeichen; belegte englische Namen ohne erfundene Umschrift; getrennte Aufgaben für Sections und Gassen. Abdeckung und Lücken sind dokumentiert. |
| Karte sinnvoll bedienen | Straßen-Hover hebt den gesamten abgefragten Verlauf hervor; Klick/Tap wählt die angezeigte Straße. Kreuzungen, Zoom, Verschieben und Touch dürfen keine falschen Antworten auslösen. |
| Lösung bis zur Antwort verbergen | Straßen-, Bezirks- und Flussnamen unabhängig einstellbar. Zielname, Hovertexte und zugängliche Steuerelementnamen verraten die Lösung nicht. |
| Vollständiges, verständliches Menü | Start, Entdecken/Lernen/Quiz, Fortschritt, Einstellungen und Hilfe sind auf Desktop und Handy erreichbar. Tastaturbedienung, verständliche Leerzustände und Rückwege werden geprüft. |
| Lokal und ohne Hostingkosten starten | Vorhandener lokaler Start und Browser-Einzeldatei bleiben verfügbar; Laufzeit benötigt keine kostenpflichtigen APIs, Konten oder externen Abrufe. |
| Ergebnisse tatsächlich in GitHub sichern | Nach abgeschlossenen, geprüften Schritten committen und pushen; abschließend lokalen und entfernten Commit vergleichen und sauberen Arbeitsbaum nachweisen. |

## Arbeitsabschnitte und Git-Regeln

1. Getesteten Ausgangsstand 0.6 als Commit sichern und pushen.
2. Straßendaten mit festen Quellenständen, Namenszuordnung, Gebietszuteilung und Abdeckungsbericht vorbereiten. Datenprüfungen bestehen lassen; danach committen und pushen.
3. Straßenmodus und Menü implementieren. Neue Funktionsprüfungen und alle vorhandenen Prüfungen ausführen. Erst einen funktionierenden, zusammengehörigen Stand committen und pushen.
4. Browser-Einzeldatei und Paket neu erzeugen, isoliert prüfen und Dokumentation an den tatsächlichen Funktionsumfang anpassen. Abschlusscommit pushen und entfernten Stand kontrollieren.

Keine Force-Pushes und keine Überschreibung fremder Änderungen. Bei zwischenzeitlichen Änderungen im entfernten Repository werden sie zuerst eingelesen und integriert. Netzwerk- und Berechtigungsprobleme werden als tatsächliche Blockaden benannt, nicht als erfolgreiche Pushes ausgegeben.

## Fachliche Entscheidungen

- Bildquiz bleibt entsprechend der bisherigen Vereinbarung eine spätere Erweiterung. Das Menü weist den Status deutlich aus und enthält keinen scheinbar funktionierenden Bildmodus.
- Namensgleiche Straßen in unterschiedlichen Städten bzw. voneinander getrennten Orten werden nicht allein aufgrund ihres Namens zusammengelegt.
- Eine Straßenaufgabe gehört zu den Bezirken, die ihr Verlauf tatsächlich berührt; die Abfrage nennt den örtlichen Kontext. Der vollständig im Datensatz vorhandene Verlauf der gewählten Einheit wird zur Auflösung gezeigt.
- Sections, Lanes und Alleys werden als eigene Einheiten behandelt. Eine übergeordnete Straße darf in der Karte als Orientierung dargestellt werden, aber nicht mit einer anders abgefragten Untereinheit verwechselt werden.
- Der Abdeckungsbericht trennt verwendbare Aufgaben von fehlenden Namen oder Geometrien. Ein kleiner Beispieldatensatz wird nicht als vollständiges Straßenangebot ausgegeben.
- Frühere Quellenvermerke über nicht direkt überprüfte amtliche Primärnamen bleiben erhalten, bis ein tatsächlicher neuer Abgleich sie ersetzt.

## Fortschritt

- [x] Vorhandenen Stand prüfen und Ausgangscommit erstellen (`ad9b634`).
- [x] Ausgangsstand auf GitHub bestätigen (`main`, `ad9b634`).
- [x] Straßendaten und Abdeckung prüfen: 22.039 Einheiten, alle 41 Bezirke, fünf bestandene Datenprüfungen. Fehlende englische Namen und ältere Geometrien ausdrücklich dokumentiert.
- [x] Straßenmodus und Menü umsetzen: Erkundung, Lernkarten, Quiz, Filter, Suche, Navigation, Hilfe, Einstellungen und Lernstand-Sicherung.
- [x] Integrationsstand prüfen: 33 gemeinsam bestandene Prüfungen; anschließend neun Straßen-/Menü-Browserprüfungen und sechs Datenprüfungen mit dem erweiterten Gassenbestand erneut bestanden.
- [ ] Lokales Paket und Einzeldatei prüfen.
- [ ] Abschlussstand pushen und entfernten Commit bestätigen.
