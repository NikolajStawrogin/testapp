# Stadt kennen · Taipei und Düsseldorf

Lokale Browser-Lernapp mit Stadtauswahl. Die bisherige Region Taipei enthält alle 41 Verwaltungsbezirke von Taipei City (12) und New Taipei City (29), vier große Flüsse und 22.240 wählbare Straßeneinheiten.
Die App läuft im Browser auf dem eigenen Rechner. Kein Konto, kein bezahltes Hosting, kein Karten-API-Schlüssel und keine externen Kartenabrufe.

## Über einen Link mit Freunden teilen

Die App ist für das kostenlose GitHub Pages im öffentlichen Repository vorbereitet. Nach einmaliger Aktivierung ist sie unter **https://nikolajstawrogin.github.io/testapp/** ohne GitHub-Konto und ohne Installation nutzbar. Die dafür nötige Repository-Einstellung und die Prüfung der Bereitstellung stehen in [GITHUB_PAGES.md](GITHUB_PAGES.md). Ein Code-Push allein aktiviert diese Einstellung nicht. Danach werden Updates auf `main` automatisch veröffentlicht.

Der Lernstand bleibt pro Browser und Website-Adresse lokal. Vorhandene lokale Lernstände können über Export/Import übernommen werden.

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

## 國語 / English · 0.13

Die App startet beim ersten Besuch in traditionellem Chinesisch. Über das Globus-Symbol oben rechts lässt sich die gesamte Oberfläche sofort auf Englisch umstellen. Die Sprachbezeichnung lautet 國語 beziehungsweise Mandarin; die Auswahl bleibt beim nächsten Besuch und Stadtwechsel erhalten. Laufende Quizrunden und Lernstände bleiben bestehen. Die Kartennamen sind separat einstellbar, Düsseldorfer Straßen behalten ihre Originalnamen. Details: [SPRACHEN.md](SPRACHEN.md).

## Straßen schrittweise lernen · 0.12

„Straßen“ startet jetzt mit Leveln: jeweils zehn neue ganze Straßen, grob nach Länge im gewählten Gebiet sortiert. Das gilt für jeden Stadtteil/Bezirk und die ganze Stadt in Düsseldorf sowie Taipei/New Taipei. Die Level-Position wird je Gebiet gespeichert. Frühere Level lassen sich zusätzlich mitüben; die bisherige Suche und Einzelwahl bleiben unter „Freie Auswahl“ erreichbar. Beispiele: Eller 13 Level, ganz Düsseldorf 290 Level. Details, Berechnungsgrenzen und Offline-Aufbereitung: [STREET_LEVELS.md](STREET_LEVELS.md).

## Was bereits funktioniert

- Startseite mit Einstiegen für Bezirke, Straßen und Flüsse. Hauptmenü mit Start, Entdecken, Lernen, Quiz, Fortschritt, Einstellungen und Hilfe; auf schmalen Bildschirmen als aufklappbares Menü.
- Straßen in allen 41 Bezirken auswählen, erkunden, als Lernkarten ansehen und im Kartenquiz finden. Straßensuche, Einzelwahl, drei Straßenklassen sowie getrennte Filter für ganze Straßen, Sections, Lanes und Alleys. Ganze Straßen wie 忠孝東路 sind zusätzlich zu ihren sieben einzelnen Sections lernbar. Im Level-Modus werden ganze Straßen verwendet. Unter „Freie Auswahl“ sind Haupt-/Verbindungsstraßen und Straßen/Sections vorbelegt; kleine Gassen können zugeschaltet werden.
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

Bildquiz, Store-Apps, Konten und Synchronisierung gehören weiterhin nicht zum implementierten Umfang. Straßenbilder werden im Menü als spätere Erweiterung erläutert. Eine PWA-Installation ist nicht eingerichtet. Die öffentliche Web-Bereitstellung wurde inzwischen vom Nutzer beauftragt und für GitHub Pages vorbereitet; die einmalige Freischaltung in den Repository-Einstellungen ist separat erforderlich. Die dokumentierten Quellen- und Rechte-Nachweisgrenzen der Namens- und Flussreferenzen bleiben transparent ausgewiesen.

Der Straßenbestand deckt beide Stadtgebiete ab, belegt jedoch keine lückenlose heutige amtliche Straßenabdeckung: Der flächendeckende OSM-Kachelstand ist von Dezember 2021, der ergänzende Innenstadt-Auszug von September 2026. Der Abdeckungsbericht nennt Aufgaben und englische Namensabdeckung je Bezirk. 1.363 wählbare Aufgaben haben keinen belegten englischen Namen. Die vollständigen Quellenkopien und ihr Hash-Manifest sind mitgeliefert. Geometrien und Namensreferenzen sind in [data/STREETS-SOURCE.md](data/STREETS-SOURCE.md) und [data/street-coverage.json](data/street-coverage.json) nachvollziehbar dokumentiert.

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

Ganze Straßen werden zusätzlich zu ihren Sections angeboten: 229 abgeleitete ganze Straßen integrieren 28 bereits vorhandene ganze Straßenstücke, insgesamt sind 22.240 Einheiten wählbar. `tools/build_street_data.py` ruft am Ende die reproduzierbare Erzeugung in `tools/build_street_parents.py` auf. Bei einer Frage zu einer ganzen Straße werden auch verräterische Section- und Gassenbeschriftungen desselben Namens verborgen.

Ein geprüftes lokales Paket einschließlich Einzeldatei, Quellenarchiven und Tests wird mit `python tools/package_app.py` erzeugt. Optional: `--output /gewünschter/pfad/app.zip --html /gewünschter/pfad/app.html`. Die Paketprüfung vergleicht alle archivierten Dateien bytegenau mit den lokalen Quellen.

## Bedienungsverbesserungen in 0.8

Die Gebietsauswahl steht groß und mittig über der Karte. Ausgewählte Namen erscheinen direkt auf der Karte; die Metro-Legende darunter ist aufklappbar und zunächst geschlossen. Die Info verdeckt keine Zoomtasten. Kartenobjekte erhalten beim Anklicken keine rechteckigen Fokusrahmen; Tastaturfokus bleibt durch eine Kontur am Objekt erkennbar.

Straßenlösungen liegen mit kräftiger grüner Linie und weißem Rand über den übrigen Kartenebenen. Andere Straßen und Metro-Linien werden während der Auflösung abgeblendet. Beim Kapitelwechsel zeigt die App eine Ladeanzeige, bevor die lokale Geometrieaufbereitung beginnt.

Zoom und Verschieben verändern sofort den bestehenden Kartenausschnitt. Eine räumliche Indizierung begrenzt die anschließende Straßensuche auf relevante Zellen; der Aufbau von Straßen und Beschriftungen erfolgt erst 120 ms nach der letzten Bewegung. Straßenbeschriftungen werden während der Bewegung kurz verborgen. Es werden beim Zoomen keine externen Kartendaten nachgeladen. Finger dürfen bis zu 30 CSS-Pixel vom Straßenverlauf entfernt sein; die Touch-Auswahl mit Bestätigung und dem Wechsel zu benachbarten Straßen bleibt erhalten. Während einer laufenden Runde ist das Gebiet gegen versehentliches Wechseln gesperrt.

## Stadtauswahl und Düsseldorf · 0.11

Wähle zuerst Taipei/New Taipei oder Düsseldorf und danach das Thema. Düsseldorf bietet eine alphabetische Auswahl von 50 Stadtteilen, 2.891 benannte Straßen-/Wegeeinheiten und sechs Flüsse: Rhein, Düssel, Nördliche und Südliche Düssel, Itter und Kittelbach. Flüsse sind einzeln mitspielbar; Flächen und Namen sind getrennt einstellbar. Quizfragen verwenden Stadtteilnamen wie Eller oder Wersten. Das große Auswahlfeld über der Karte grenzt auch Straßen und Flüsse nach Stadtteilen ein. Mehrere Stadtteile lassen sich in der Liste für eine gemeinsame Runde wählen. Suche, Lernkarten, Quiz, Touch-Auswahl, Fehlerwiederholung und regionale Lernstände nutzen dieselbe App. Frühere Nummern-Auswahlen werden in die zugehörigen Stadtteile übertragen.

26 archivierte Bahnlinien dienen zur Orientierung: zwölf U-Bahn-/Stadtbahnlinien, sechs S-Bahnlinien, sieben Straßenbahnlinien und SkyTrain. Die vier Bahnarten lassen sich einzeln ein-/ausblenden. Sie verbinden belegte VRR-Haltestellen schematisch; es sind keine exakten Gleiskurven und keine Echtzeitfahrplandaten. Die Legende zeigt diese Einschränkung ausdrücklich.

Die benötigten Daten stammen aus fest versionierten öffentlichen Archiven. Für diese Version ist keine Cloud-Netzwerkfreigabe durch den Nutzer erforderlich. Herkunft, Nutzungsbedingungen und Datenstände stehen in [REGIONEN.md](REGIONEN.md). Straßen- und Gebietsquellen sind historisch; ein aktuelles amtliches Straßenverzeichnis wird nicht behauptet. Fehlende Straßenklassen bleiben als unbekannt erkennbar.

Nur das Paket der gewählten Region wird geladen. Einstellungen und Lernstände sind getrennt; alte Taipei-Lernstände bleiben erhalten. Der Offline-Export enthält beide Regionen. `python tools/build_duesseldorf_layers.py` und danach `python tools/build_duesseldorf_data.py` bauen Düsseldorf ohne Netzwerk neu auf; dafür wird Shapely 2.1.2 benötigt. `python tools/package_app.py` erstellt das vollständige ZIP einschließlich Originalkopien und Tests.
