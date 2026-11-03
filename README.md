# Taipei kennen

Lokale Browser-Lernapp 0.7 für alle 41 Verwaltungsbezirke von Taipei City (12) und New Taipei City (29), vier große Flüsse und 22.039 benannte Straßeneinheiten.
Die App läuft im Browser auf dem eigenen Rechner. Kein Konto, kein bezahltes Hosting, kein Karten-API-Schlüssel und keine externen Kartenabrufe.

## Lokal starten

### Einfacher Start im Browser

Im fertigen Downloadpaket die Datei `Taipei-kennen.html` im Browser öffnen. Sie enthält App, Kartendaten, Metro-Linien und Gestaltung in einer Datei. Für diese Startart sind keine Installation, kein Python, kein Server und keine Internetverbindung erforderlich. Die Datei wird bei der Paket-Erzeugung gebaut und nicht doppelt im Git-Repository gespeichert.

Aus dem GitHub-Quellpaket alternativ `index.html` zusammen mit den vollständig entpackten Unterordnern öffnen oder den unten beschriebenen lokalen Server starten. Eine vom verwendeten Client angebotene Webvorschau kann dieselben statischen Dateien anzeigen; ihre Verfügbarkeit hängt vom Client ab.

Der Lernstand der bisherigen lokalen Server-Version wird beim Wechsel zur Datei nicht automatisch übernommen. Für die weitere Nutzung eines vorhandenen Server-Lernstands weiterhin denselben Browser und die bisherige lokale Adresse verwenden.

### Start über einen lokalen Server

Alternativ: Python 3 und ein moderner Desktop-Browser. Für diese Startart sind keine zusätzlichen Python-Pakete oder Node.js nötig.

### Windows

1. Das ZIP-Paket vollständig entpacken.
2. `Start.bat` im entpackten Ordner doppelklicken.
3. Der Browser öffnet die lokale App. Das Konsolenfenster während der Nutzung geöffnet lassen.

Falls Python fehlt, meldet die Startdatei dies. Python 3 ist kostenlos über [python.org](https://www.python.org/downloads/) erhältlich. Danach die Startdatei erneut öffnen.

### Über das Terminal

Im Projektordner:

```sh
python server.py
```

Unter Windows ist alternativ `py -3 server.py` möglich. Der Server bindet ausschließlich an die lokale Adresse `127.0.0.1`, standardmäßig Port 8765. Beenden mit Strg+C.

Ist der Port bereits belegt, lässt sich ein anderer auswählen:

```sh
python server.py --port 8766
```

Die App funktioniert nach dem Bereitstellen der Dateien ohne Internetverbindung. Die optionalen Quellenlinks benötigen beim Öffnen Internetzugriff.

## Was bereits funktioniert

- Startseite mit Einstiegen für Bezirke, Straßen und Flüsse. Hauptmenü mit Start, Entdecken, Lernen, Quiz, Fortschritt, Einstellungen und Hilfe; auf schmalen Bildschirmen als aufklappbares Menü.
- Straßen in allen 41 Bezirken auswählen, erkunden, als Lernkarten ansehen und im Kartenquiz finden. Straßensuche, Einzelwahl, drei Straßenklassen sowie getrennte Filter für Straßen, Sections, Lanes und Alleys. Standardmäßig sind Haupt-/Verbindungsstraßen und Straßen/Sections gewählt; kleine Gassen können schrittweise zugeschaltet werden.
- Maus-Hover hebt die gesamte gewählte Straßeneinheit hervor, ein Klick wählt sie. Auf Touch-Geräten wird die angetippte Straße zuerst hervorgehoben und anschließend bestätigt. An Kreuzungen ist zwischen nahen Straßen wechselbar. Verschieben und Zoomen geben keine Quizantwort ab. Der Zielname bleibt vor der Auflösung verborgen.
- Straßenfilter und Einzelauswahl werden gespeichert. Fehlende englische Namen sind ausdrücklich gekennzeichnet und standardmäßig aus dem Quiz ausgeschlossen; reine Englisch-Aufgaben enthalten keine erfundenen Ersatznamen. Die Namensherkunft ist dokumentiert und keine pauschale Zusage heutiger amtlicher Verifikation.
- Lernstand als JSON sichern und nach ausdrücklicher Bestätigung wieder einlesen. Ungültige Dateien werden abgewiesen; ein Import beendet gegebenenfalls die laufende Runde. Fortschritt, Fehlerwiederholung und Lernkarten funktionieren auch für Straßen.
- Tamsui, Keelung, Xindian und Dahan als blaue Flussflächen zur Orientierung anzeigen. „Flüsse anzeigen“ und „Flussnamen anzeigen“ sind unabhängig vom Mitüben und von den Bezirksnamen einstellbar; die Auswahl wird gespeichert.
- Mit „Flüsse mitüben“ die Flüsse für Lernkarten und Quiz aktivieren und einzeln auswählen. Für reine Flussrunden die Bezirksauswahl aufheben; ansonsten entstehen gemischte Runden. Es zählen nur die im gewählten Stadtgebiet enthaltenen Flüsse (Taipei: drei, New Taipei: vier). Die richtige Flussfläche wird nach der Antwort markiert, der Zielname vorher verborgen. In Flussfragen ist die Flussebene immer sichtbar. Richtige und falsche Flussantworten, Fehlerwiederholung und Lernfortschritt funktionieren wie bei Bezirken; Lernkarten werden nicht bewertet.
- Alle 41 Bezirke auf einer zoombaren und verschiebbaren Karte erkunden.
- Unter „Gebiet“ beide Städte, Taipei City oder New Taipei City wählen. Die Bezirksliste ist nach Stadt gruppiert und scrollbar.
- Über „Auswahl zeigen“ den Kartenausschnitt auf die ausgewählten Bezirke ausrichten. Kleine Bezirksnamen erscheinen beim Hineinzoomen; Beschriftungen bleiben dabei lesbar.
- Metro- und Stadtbahnlinien als Orientierung: 12 Linienkennungen einschließlich Kreislinie, Flughafen-MRT, Danhai-, Ankeng- und Sanying-Linie sowie der Abzweige, mit Legende und geografischen Verläufen innerhalb beider Städte. Über „Metro-Linien anzeigen“ auch im Quiz abschaltbar; die Auswahl bleibt nach Neuladen erhalten.
- Zoom von 50 bis 1200 Prozent für Bezirke und Flüsse, im Straßenmodus bis 9600 Prozent, per Mausrad, Plus/Minus oder Zoomregler. Zurücksetzen stellt die Übersicht des gewählten Gebiets wieder her. „Auswahl zeigen“ richtet den Straßenmodus auf die gewählten Bezirke aus.
- Touch-Steuerung: zwei Finger auseinander- oder zusammenziehen zum Zoomen, ein Finger zum Verschieben, kurz antippen zum Auswählen. Zoomen und Verschieben zählen nicht als Quizantwort.
- Einzelne oder mehrere Bezirke auswählen und beide Städte gemeinsam oder getrennt üben. Die jeweilige Stadt erscheint bei Aufgabe, Auflösung und Fortschritt.
- Lernkarten mit anschließender Auflösung auf der Karte.
- Kartenquiz mit standardmäßig zehn unterschiedlichen Aufgaben; bei kleinerer Auswahl entsprechend weniger. „Alle gewählten Bezirke“ unterstützt auch komplette Runden mit 29 oder 41 Aufgaben.
- Richtige und falsche Antworten vergleichen und Fehler erneut üben.
- Traditionelles Chinesisch, Englisch oder beide Schreibweisen anzeigen.
- Unter „Bezirksnamen auf der Karte“ die Namen für Taipei City und New Taipei City unabhängig ein- und ausblenden. So können beim Taipei-Quiz nur die New-Taipei-Namen als Orientierung sichtbar bleiben, auch außerhalb der Aufgabenauswahl. Die Einstellungen werden gespeichert; der gesuchte Bezirk bleibt vor der Antwort unbeschriftet. Kleine Bezirksnamen erscheinen beim Hineinzoomen.
- Quizfortschritt lokal im Browser speichern, nach Neuladen ansehen und löschen. Bestehende Taipei-Lernstände werden übernommen; die bisherige Gesamtauswahl der zwölf Bezirke wird beim ersten Wechsel auf beide Städte erweitert.

Der Fortschritt gehört zum verwendeten Browser und zur lokalen Adresse. Für denselben Fortschritt weiterhin denselben Browser und Port verwenden. Ein privates Browserfenster oder das Löschen der Browserdaten kann den Fortschritt entfernen. Es gibt keine Synchronisation.

## Noch nicht enthalten

Bildquiz, Store-Apps, Konten und Synchronisierung gehören weiterhin nicht zum implementierten Umfang. Straßenbilder werden im Menü als spätere Erweiterung erläutert. Eine eigene Online-Bereitstellung oder PWA-Installation ist noch nicht eingerichtet. Die App bleibt statisch und kann später auf kostenlosem statischem Hosting bereitgestellt werden; aktuelle Rechtefragen der Namens- und Flussreferenzen müssen vor einer öffentlichen Veröffentlichung abschließend geklärt werden.

Der Straßenbestand deckt beide Stadtgebiete ab, belegt jedoch keine lückenlose heutige amtliche Straßenabdeckung: Der flächendeckende OSM-Kachelstand ist von Dezember 2021, der ergänzende Innenstadt-Auszug von September 2026. Der Abdeckungsbericht nennt Aufgaben und englische Namensabdeckung je Bezirk. 1.362 Aufgaben haben keinen belegten englischen Namen. Die vollständigen Quellenkopien und ihr Hash-Manifest sind mitgeliefert. Geometrien und Namensreferenzen sind in [data/STREETS-SOURCE.md](data/STREETS-SOURCE.md) und [data/street-coverage.json](data/street-coverage.json) nachvollziehbar dokumentiert.

Die Bezirksgeometrien sind ein vereinfachter, älterer Referenzbestand aus dem unter CC0 bereitgestellten Projekt `g0v/twgeojson`. Ein Abgleich mit aktuellen amtlichen Grenzen steht aus. Die Namensreferenz ist in [OFFIZIELLE_NAMEN.md](OFFIZIELLE_NAMEN.md) mit ihren Nachweisgrenzen beschrieben. Dieser Prototyp ist keine amtliche Karten- oder Grenzauskunft.

Die vier Flüsse stammen aus einem veröffentlichten Auszug von Flussflächen der taiwanischen Water Resources Agency. Herkunft, Geometriebearbeitung und Grenzen der Prüfung sind in [data/RIVERS-SOURCE.md](data/RIVERS-SOURCE.md) dokumentiert. Die Darstellung ist auf beide Städte begrenzt; Flüsse setzen sich außerhalb fort. Chinesische Namen stammen aus den Namensattributen, englische Namen wurden ergänzt und sind noch nicht erneut amtlich abgeglichen.

Die Metro-Geometrien stammen aus dokumentierten OpenStreetMap-Auszügen von Juni bis September 2026. Die Anzeige ist auf die dargestellten Grenzen beider Städte begrenzt. Originaldaten und ODbL-Hinweis liegen in `data/metro-routes-source.geojson`, `data/metro-extra-source/` und `data/METRO-LICENSE.md`. Kartenanzeige und Zoom laden auch mit aktivierter Metro-Ebene keine externen Daten nach.

## Dokumentation

- [Anforderungen](ANFORDERUNGEN.md)
- [Kartenvergleich](KARTENQUELLE.md)
- [Namensrecherche](OFFIZIELLE_NAMEN.md)
- [Datenquellen und Rechtehinweise](THIRD_PARTY_NOTICES.md)
- [Straßenquelle und Namenszuordnung](data/STREETS-SOURCE.md)
- [Ziele, Prüfkriterien und Git-Zwischenstände](UMSETZUNGSPLAN.md)

## Entwicklung und Prüfung

Die App nutzt HTML, CSS, JavaScript und lokale SVG-Geometrien, einschließlich MultiPolygon-Flächen und MultiLineString-Straßen. `street-map.js` zeichnet den sichtbaren Kartenausschnitt, hebt vollständige Einheiten hervor und bestimmt nahe Straßen geometrisch. Lokale Straßendetails erscheinen beim Hineinzoomen. Zur Laufzeit werden keine Kartenkacheln oder Bibliotheken nachgeladen. Die Erzeugungsskripte in `tools/` benötigen die dokumentierten ursprünglichen Quelldateien; diese sind keine Laufzeitvoraussetzung.

Die Browser-Einzeldatei lässt sich aus den vorhandenen App-Dateien mit `python tools/export_standalone.py` neu erzeugen. Dieser Export benötigt keine zusätzlichen Pakete. Die Skripte werden in ihrer bisherigen Reihenfolge am Ende des Dokuments eingebettet, damit die Oberfläche vor ihrer Ausführung vorhanden ist.

Ein reproduzierbarer Browser-Funktionstest liegt in `tests/test_browser.py`. Er benötigt für die Entwicklung Playwright und Chromium, die nicht Bestandteil der Laufzeitabhängigkeiten der App sind:

```sh
python -m unittest discover -s tests -v
```

Der Test startet seinen eigenen lokalen Dateiserver und prüft Kartenklicks auf alle 41 Flächen, Mausrad, Zoomregler, Quizbewertung, Fehlerwiederholung, Lernkarten, Drag-Verhalten, Fortschritt und Löschung. Weitere Prüfungen decken unabhängige Bezirksbeschriftungen beider Städte (einschließlich Orientierung außerhalb des Quizgebiets, verborgener Lösung und Speicherung), getrennte Stadtgebiete, eine vollständige 29-Aufgaben-Runde, gemischte Aufgaben und die Übernahme alter Einstellungen und Lernstände ab. Für die Metro-Ebene prüft er Sichtbarkeit, Speicherung, Sprache, gemeinsame Projektion und Kartenklicks durch eine Linie auf den darunterliegenden Bezirk. Eine mobile Browseremulation prüft mit aktivierter Metro zusätzlich Zweifinger-Zoom in beide Richtungen, Verschieben, abgebrochene Touch-Gesten und anschließendes Antippen ohne versehentliche Antworten. Für die Flüsse werden Orientierungsebene und Namensschalter, Einzel-/Stadtauswahl, reine und gemischte Quizrunden, Lernkarten, Wertung, Fehlerwiederholung, Speicherung, Treffererkennung am Zusammenfluss sowie Touch-Zoom, Verschieben und anschließendes Antippen geprüft. JavaScript-Fehler und externe Netzwerkaufrufe führen zum Fehlschlag. Über `TAIPEI_CHROMIUM` kann ein abweichender Chromium-Pfad angegeben werden.

Geprüft in dieser Cloud-Umgebung mit Chromium auf Linux, für Touch in mobiler Emulation. Tests auf einem realen Smartphone und auf dem Rechner des Nutzers stehen aus. Die Windows-Startdatei ist beigefügt.

Die zusätzlichen Prüfungen in `tests/test_streets_browser.py` behandeln Straßenquiz, Hover und Lösungsverdeckung, Fehlerwiederholung, Lernkarten und Tastatur, Sections/Lanes/Alleys, äußere New-Taipei-Bezirke, fehlende englische Namen, Menüwechsel, Einstellungen, Sicherung und Import sowie Touch-Gesten und Straßenauswahl an Kreuzungen. Sämtliche Browserprüfungen laufen auch bei aktivierter Metro-Ebene.

Für die Datenprüfungen allein werden keine Zusatzpakete benötigt: `python -m unittest discover -s tests -p test_street_data.py -v`. Zum erneuten Erzeugen des Straßenkatalogs aus dem mitgelieferten Quellenarchiv benötigen ausschließlich die Entwicklungswerkzeuge `mapbox-vector-tile` und `shapely`; danach `python tools/build_street_data.py` ausführen. Jeder archivierte Datenteil wird vorher gegen seine Prüfsumme geprüft.
