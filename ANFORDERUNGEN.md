# Anforderungen: Taipei City und New Taipei City lernen

Stand: 3. November 2026. Status: lokale Lernapp 0.7 mit Bezirken, Flüssen, Straßen und vollständiger Navigation umgesetzt. Die dokumentierten Grenzen von Quellenaktualität, amtlicher Namensverifikation und Vollständigkeit bleiben bestehen.
Nach dem Umgebungswechsel aus den im Gespräch bestätigten Anforderungen wiederhergestellt.

## Ziel und Umfang

Die Browser-App hilft dem Nutzer, erwähnte Straßennamen in Taipei City und New Taipei City räumlich einzuordnen und die Straßen auf einer Karte zu finden. Eine vorgelagerte Lernstufe vermittelt die Verwaltungsbezirke. Später soll die Erkennung von Straßen anhand von Straßenbildern hinzukommen.

- Erste Zielgruppe ist der Nutzer selbst. Öffentliche Nutzung bleibt eine spätere Erweiterung.
- Der Geltungsbereich umfasst Taipei City und New Taipei City mit insgesamt 41 Verwaltungsbezirken (12 + 29).
- Erste Version lokal im Browser auf dem vorhandenen Rechner des Nutzers. Die Karte unterstützt zusätzlich Touch-Gesten; eine eigenständige Smartphone-Bereitstellung bleibt eine spätere Erweiterung.
- Die Entwicklung startet auf Basis der abgestimmten Anforderungen mit einem lokalen Bezirksprototyp. Offene Datenfragen und der vollständige Straßenumfang bleiben dokumentiert.

## Verbindliche Kostenvorgabe

- Hostinggebühren sind ausgeschlossen: 0 Euro zusätzliche Hostingkosten für die vereinbarte Nutzung.
- Kostenpflichtige Hostingdienste sind keine Voraussetzung für die erste Version. Bei Erreichen eines kostenlosen Kontingents darf keine automatische kostenpflichtige Erweiterung erfolgen.
- Bestätigtes Bereitstellungsmodell ist eine lokal laufende Browser-App auf dem Rechner des Nutzers. Ein gemieteter Server oder eine öffentliche Bereitstellung wird in der ersten Version nicht benötigt.
- Taipei-Kartendaten und benötigte Darstellungsdateien lokal mitzuliefern bleibt der technische Planungsvorschlag; Quelle, Umfang und Ladeverhalten sind noch zu prüfen. Lokaler Betrieb bedeutet nicht automatisch vollständig geprüfte Offline-Fähigkeit.

## Bestätigte Anforderungen

### Gebiete und Lerngegenstand

- Alle 41 offiziellen Verwaltungsbezirke bilden die Gebietsauswahl. Beide Städte gemeinsam, eine einzelne Stadt sowie beliebige Bezirke innerhalb des gewählten Stadtgebiets sind auswählbar. Die Auswahl ist nach Städten gruppiert; jede Aufgabe nennt ihre Stadt.
- Gegenden wie 東湖 (Donghu) innerhalb von 內湖區 (Neihu District) bleiben eine spätere zusätzliche Auswahlmöglichkeit. Umgangssprachliche Gegenden sind nicht automatisch deckungsgleich mit offiziellen Verwaltungseinheiten.
- Lern- und Quizmodus unterstützen Verwaltungsbezirke sowie Straßen als getrennte Lerngegenstände.
- Große Flüsse strukturieren die Karte als zuschaltbare blaue Orientierungsebene. Zunächst enthalten: Tamsui (淡水河), Keelung (基隆河), Xindian (新店溪) und Dahan (大漢溪).
- Flüsse können unabhängig von ihrer Namensanzeige zum Mitüben aktiviert und einzeln ausgewählt werden. Reine Flussrunden und gemischte Bezirks-/Flussrunden sind in Lernkarten und Quiz möglich. Die Gebietsauswahl begrenzt die Aufgaben auf dort enthaltene Flüsse. Bezirksnamen- und Flussnamenanzeigen sind unabhängig einstellbar und werden lokal gespeichert.
- Bei Flussfragen bleibt der Zielname vor der Auflösung verborgen. Eine Antwort wählt einen Flusslauf statt einer Bezirksfläche. Zoomen, Verschieben und Einstellungen geben keine Antwort ab. Auch schmale Flächen sind per Maus und Touch treffbar; an Zusammenflüssen hat die tatsächliche Wasserfläche Vorrang vor der erweiterten Trefferfläche eines anderen Flusses. Lösung, Wertung, Fehlerwiederholung und lokaler Fortschritt unterstützen beide Aufgabentypen.
- Grundsätzlich sind Straßen aller Größen bis zu kleinen Straßen, Lanes und Alleys vorgesehen. Der Nutzer kann den gewünschten Straßenumfang auswählen. Die tatsächliche Datenabdeckung ist noch nachzuweisen.
- Nummerierte Sections sowie einzelne Lanes und Alleys können eigene Quizaufgaben sein.

### Namen und Sprache

- Traditionelle chinesische Zeichen und die in Taiwan verwendete offizielle englische Umschrift.
- Standardmäßig beide Schreibweisen zusammen; wahlweise eine der beiden ausblenden.
- Maßgebliche amtliche Quelle und Umgang mit Schreibvarianten sind noch zu prüfen. Fehlende englische Namen werden nicht durch ungeprüfte automatische Umschrift ersetzt.
- Die vertiefte Recherche in [OFFIZIELLE_NAMEN.md](OFFIZIELLE_NAMEN.md) identifiziert Postverzeichnisse als bevorzugten Kandidaten. Inhalte öffentlich gespiegelter Dateien wurden geprüft; aktuelle Primärdateien, Rechte und Übereinstimmung mit städtischen Schreibweisen bleiben zu verifizieren. Landesweite Namenspaare ersetzen keine Taipei-Geometrien oder vollständigen Lane-/Alley-Katalog.

### Lernen und Quiz

- Lernmodus mit freier Kartenerkundung und Lernkarten.
- Bezirksquiz: Bezirksname erscheint, der Nutzer klickt auf den Bezirk; anschließend wird die richtige Bezirksfläche hervorgehoben.
- Straßenquiz: Straßenname erscheint, der Nutzer wählt die gesuchte Straße durch Kartenklick; anschließend wird der richtige Verlauf der abgefragten Einheit angezeigt.
- Karte zoombar. Beim Überfahren einer auswählbaren Straße mit der Maus wird deren Verlauf vor der Antwort hervorgehoben. Die Hervorhebung gibt nicht vorweg, ob die Straße richtig ist.
- Die Karte unterstützt auch Zweifinger-Zoom und Verschieben mit einem Finger. Ein kurzer Tipp wählt einen Bezirk; Verschieben, Zoomen und abgebrochene Gesten geben keine Quizantwort ab.
- Der Klick wählt die hervorgehobene Straße. Eine geografische Entfernungsschätzung ist nicht als Nutzeraufgabe vorgesehen. Die Anwendung benötigt trotzdem eine zuverlässige Treffererkennung an dünnen Linien und Kreuzungen.
- Ob andere Straßennamen als Orientierung sichtbar sind, ist auswählbar.
- Bezirksnamen lassen sich für Taipei City und New Taipei City unabhängig ein- und ausblenden, auch außerhalb der gewählten Quizbezirke. Beim Taipei-City-Quiz können somit nur die New-Taipei-Namen als Orientierung sichtbar bleiben und umgekehrt. Die Einstellungen werden lokal gespeichert; der gesuchte Name bleibt bis zur Auflösung verborgen.
- Metro-Linien strukturieren die Karte als Orientierungshilfe. Die Ebene ist standardmäßig sichtbar, in allen Modi abschaltbar und bleibt mit Zoom und Touch geografisch ausgerichtet. Die Sichtbarkeit wird lokal gespeichert. Gezeigt werden verfügbare Metro- und Stadtbahnabschnitte innerhalb beider Städte, einschließlich Kreislinie, Flughafen-MRT und Stadtbahnen in New Taipei, mit Linienfarben und Legende. Die Quellenstände werden dokumentiert.
- Quiz standardmäßig zehn Aufgaben; anschließend falsch beantwortete Aufgaben erneut üben.

### Datenschutz und Fortschritt

- Erste persönliche Version ohne Konto sowie ohne Analyse- oder Werbetracker.
- Lernfortschritt lokal im Browser speichern und eine Löschfunktion anbieten.
- Fortschritt bleibt nach Neuladen im selben Browser erhalten. Beim Löschen des Browserspeichers kann er verloren gehen; keine Synchronisation vorgesehen.

### Spätere Erweiterung

- Weitergehende Smartphone-Anpassungen, eigenständige Smartphone-Bereitstellung und gegebenenfalls öffentliche Bereitstellung. Grundlegende Touch-Kartenbedienung ist bereits gefordert. Vor öffentlicher Bereitstellung ist die Kostenvorgabe erneut zu berücksichtigen.
- Straßenbild ansehen und Straße benennen; in der ersten Version nicht implementieren.
- Google Street View ist dafür ein Kandidat, noch keine bestätigte Bildquelle. Kosten, Nutzungsbedingungen und Kombination mit der Kartenquelle separat prüfen.

## Vorgesehener Ablauf

1. App öffnen.
2. Verwaltungsbezirke oder Straßen wählen; Lernen oder Quiz auswählen.
3. Bei Straßen Gebiet und Straßenumfang auswählen.
4. Namenanzeige und Kartenbeschriftung einstellen.
5. Lernen beziehungsweise Quiz starten.
6. Im Quiz antworten, Lösung ansehen und nach der Runde Fehler wiederholen.

## Vorschläge, noch nicht bestätigt

- Keine Standortfreigabe erforderlich.
- Externe Karten- und Datenanbieter sowie deren Verarbeitung technischer Zugriffsdaten transparent benennen.
- Gesuchten Straßen- beziehungsweise Bezirksnamen auch bei aktivierten Orientierungshilfen auf der Karte verbergen. Technische Machbarkeit und andere mögliche Lösungshinweise prüfen.

## Vorläufige Akzeptanzkriterien

1. Gebietsauswahl enthält die zwölf Verwaltungsbezirke von Taipei City und die 29 Verwaltungsbezirke von New Taipei City. Beide Städte, jede Stadt einzeln und einzelne Bezirke sind wählbar; Donghu bleibt eine spätere zusätzliche Gebietseinteilung.
2. Straßenaufgaben berücksichtigen gewähltes Gebiet und Straßenumfang. Grenzfälle werden nach einer vor Umsetzung festzulegenden Regel behandelt.
3. Jede verwendete Aufgabe besitzt eine eindeutig identifizierte Bezirksfläche beziehungsweise Straßengeometrie sowie nachvollziehbar belegte traditionelle chinesische und offizielle englische Namen. Fehlende Angaben werden nicht erfunden.
4. Sections, Lanes und Alleys können als getrennte Aufgaben geführt werden, ohne nur wegen gleicher Namensbestandteile zusammenzufallen.
5. Lernen und Quiz sind für Bezirke und Straßen getrennt startbar; freie Erkundung und Lernkarten sind verfügbar.
6. Zoom funktioniert; Maus-Hover hebt die auswählbare Straße hervor; ein Klick wählt diese. Anschließend erscheint der richtige Verlauf. Im Bezirksquiz erscheint die richtige Bezirksfläche.
7. Andere Straßennamen lassen sich auf der Quizkarte ein- und ausblenden.
8. Standardrunde hat zehn Aufgaben, sofern ausreichend Aufgaben vorhanden sind; anschließende Fehlerwiederholung ist möglich.
9. Beide Namensschreibweisen sind standardmäßig sichtbar und jeweils einzeln ausblendbar.
10. Gebietsauswahl, Lernen, Quizantwort und Auswertung sind im Desktop-Browser auf dem Rechner des Nutzers bedienbar. Die Karte unterstützt zusätzlich Antippen, Verschieben mit einem Finger und Zweifinger-Zoom ohne versehentliche Quizantworten; eine eigenständige Smartphone-Bereitstellung ist nicht erforderlich.
11. Nutzung benötigt kein Konto, enthält keine Analyse- oder Werbetracker und bietet lokale Fortschrittsspeicherung sowie deren Löschung.
12. Kein aktiver Bildquizmodus in der ersten Version.
13. Der vereinbarte Betrieb erfordert kein bezahltes Hosting. Kostenlose Kontingente dürfen bei Überschreitung keine automatischen Gebühren auslösen.
14. Die erste Version wird auf dem Rechner des Nutzers gestartet und lokal im Browser geöffnet. Ein öffentlicher Server, Smartphone-Zugang oder eine Veröffentlichung ist dafür nicht erforderlich.
15. Die Metro-Ebene lässt sich während Erkundung, Lernkarten und Quiz ein- und ausblenden, ohne eine Antwort abzugeben oder den Kartenausschnitt zurückzusetzen. Sie verschiebt und skaliert sich zusammen mit der Bezirkskarte, verdeckt keine Kartenklicks und benötigt keine externen Abrufe. Nach Neuladen gilt die letzte Sichtbarkeitseinstellung.

16. Bereits gespeicherte Taipei-Lernstände bleiben erhalten. Eine bisherige Gesamtauswahl aller zwölf Taipei-Bezirke wird auf beide Städte erweitert; ausdrücklich eingeschränkte Auswahlen bleiben erhalten. „Alle gewählten Bezirke“ ist dynamisch und funktioniert auch mit 29 oder 41 Aufgaben.
17. Kartenansicht und „Auswahl zeigen“ lassen sich auf das gewählte Gebiet ausrichten. Beschriftungen kleiner Bezirke werden beim Hineinzoomen lesbar, ohne dass der gesuchte Name vor einer Quizantwort eingeblendet wird.
18. Die beiden Stadtschalter für Bezirksnamen funktionieren unabhängig von Gebietsauswahl, Lernmodus und voneinander. Änderungen geben keine Quizantwort ab und setzen den Kartenausschnitt nicht zurück. Nicht ausgewählte Bezirke bleiben trotz sichtbarer Namen von der Antwortauswahl ausgeschlossen. Bestehende globale Einstellungen zur Namenssichtbarkeit werden für beide Städte übernommen.

## Festgelegte Bedienungsregeln und verbleibende Datenprüfung

Die Bedienungsregeln für Version 0.7 sind festgelegt: Drei Straßenklassen folgen der OSM-Straßenfunktion, unabhängig von der Unterteilung in Straßen, Sections, Lanes und Alleys. Verläufe werden nach Stadt, Namen und örtlichem Zusammenhang unterschieden. Berührte Bezirke sind auswählbar; gleichnamige kartierte Teilstücke innerhalb eines Bezirks bilden eine Aufgabe. Maus-Hover hebt den vollständigen Verlauf hervor, der Klick wählt ihn. Touch zeigt zunächst eine Vorschau mit Bestätigung und erlaubt an Kreuzungen den Wechsel zu anderen nahen Straßen. Die Standardrunde hat zehn Aufgaben oder weniger bei kleinerem Angebot. Lernkarten zählen nicht als Quizantworten. Konkrete Quellaktualität und amtliche Primärnamen bleiben Prüfaufgaben.

- Die heutigen amtlichen Namensverzeichnisse müssen noch direkt mit den verwendeten Postreferenz-Kopien abgeglichen werden; insbesondere ist keine pauschale aktuelle amtliche Bestätigung aller zusammengesetzten Gassennamen erbracht.
- Die aktuelle amtliche Straßen- und Bezirksvollständigkeit muss unabhängig vom nachgewiesenen enthaltenen Bestand geprüft werden. Bauänderungen und OSM-Lücken können im älteren flächendeckenden Bestand fehlen.
- Vor einer öffentlichen Bereitstellung sind die aktuellen Weiterverwendungsbedingungen der Namens- und Flussreferenzen abschließend zu klären. Der lokale persönliche Betrieb benötigt keine kostenpflichtigen Karten-APIs.

## Datenprüfung und Kartenwahl

Die Entscheidungsvorlage steht in [KARTENQUELLE.md](KARTENQUELLE.md).

Vorläufig empfohlen: MapLibre für die Darstellung, OSM-basierte Straßenverläufe und separat geprüfte amtliche Namen und Bezirksgrenzen. Daten und benötigte Darstellungsdateien sollen für die vorgeschlagene lokale Variante mitgeliefert werden. Noch keine verbindliche Anbieterwahl. Abdeckung bis zu Lanes und Alleys, amtliche englische Namen, Lizenzen und eine Bereitstellung ohne Hostinggebühren müssen geprüft werden.

## Abgrenzung

Bildquiz, Store-Apps, öffentliche Nutzerkonten und Synchronisation gehören nicht zur ersten Version. Der lokale Betrieb bleibt erhalten. Ergänzend hat der Nutzer am 3. November 2026 die kostenlose öffentliche Bereitstellung über GitHub Pages beauftragt. Freunde sollen die App ohne GitHub-Konto über einen Link öffnen können; Details und notwendige einmalige Repository-Einstellung stehen in `GITHUB_PAGES.md`.

## Stand des ersten Prototyps

Die 41 Bezirke beider Städte sind als lokale Karte mit freier Erkundung, Lernkarten und Quiz umgesetzt. Gebietsauswahl, Zoom einschließlich Zweifinger-Geste, Metro-Orientierungsebene, Fehlerwiederholung, Sprachenwahl und lokaler Quizfortschritt sind vorhanden. Start über `Start.bat` beziehungsweise `python server.py`; Details in [README.md](README.md).

Version 0.6 ergänzt die vier großen Flüsse als Orientierung und optionale Lernaufgaben. Im Bezirksquiz lassen Flüsse Kartenklicks durch; während einer Flussfrage sind nur die gewählten Flüsse antwortbar und ihre Flächen immer sichtbar. Fluss-Namensanzeige und Teilnahme werden unabhängig gespeichert. Quellen- und Namensnachweisgrenzen stehen in `data/RIVERS-SOURCE.md`.

Version 0.7 setzt Straßen-Erkundung, Lernkarten und Quiz für 22.240 Einheiten einschließlich aus Sections abgeleiteter ganzer Straßen in allen 41 Bezirken um. Gebiet, Straßenklassen, Namenseinheiten, Suchbegriff und Einzelaufgaben sind wählbar. Das Hauptmenü bietet Start, Entdecken, Lernen, Quiz, Fortschritt, Einstellungen und Hilfe, einschließlich mobilem Menü und Lernstand-Sicherung. `data/STREETS-SOURCE.md` und der Abdeckungsbericht belegen den verwendeten Bestand und benennen Lücken. Der flächendeckende Geometriestand ist älter (2021), der Innenstadt-Auszug neuer (2026). Ein heutiger amtlicher Vollständigkeitsnachweis, der aktuelle Originalabgleich aller englischen Namen und der abschließende Rechteabgleich für eine öffentliche Veröffentlichung sind damit weiterhin nicht erbracht.

## Bedienbarkeit und Kartenleistung · Ergänzung 0.8

- Nach einer falschen Straßenantwort muss die vollständige richtige Straßeneinheit klar erkennbar sein: kräftige grüne Linie mit weißem Rand über den Kartenebenen; übrige Straßen und Metro treten zurück.
- Ein Klick auf ein Kartenobjekt darf keinen rechteckigen Fokusrahmen erzeugen. Tastaturbedienung und eine am Objekt erkennbare Fokusmarkierung bleiben erhalten.
- Namen und Lage der Auswahl werden in einer Infobox direkt innerhalb der Karte angezeigt, vor der Metro-Legende und auf kleinen Displays ohne Überdeckung der Zoomtasten.
- Die Metro-/Stadtbahnlegende ist aufklappbar und nach dem Öffnen der App standardmäßig geschlossen.
- Beim Wechsel von Startseite oder Themenauswahl in die Karte erscheint vor der lokalen Geometrieaufbereitung eine sichtbare Ladeanzeige. Eine erfundene Prozentangabe ist nicht erforderlich.
- Während Zoom und Verschieben darf nicht für jedes Eingabeereignis der Straßen-DOM neu aufgebaut werden. Der Kartenausschnitt wird sofort transformiert; aufwendige Straßendetails werden nach Ende der Bewegung erneuert. Eine räumliche Indizierung beschränkt die Suche auf relevante Kartenzellen. Externe Nachladeabrufe sind weiterhin ausgeschlossen.
- Die geografische Finger-Trefferzone bleibt unabhängig vom Zoom mindestens 30 CSS-Pixel im Radius. Nahe Straßen können vor der endgültigen Quizantwort gewechselt und bestätigt werden; Pinch und Ziehen dürfen keine Antworten abgeben.
- „Taipei City“, „New Taipei City“ und „beide Städte“ werden über ein mindestens 44 Pixel hohes Auswahlfeld mittig über der Karte gewählt. Während einer laufenden Runde bleibt das gewählte Gebiet gesperrt.

## Mehrere Lernregionen · Erweiterung 0.9

Der Nutzer hat beide Düsseldorfer Gebietsebenen sowie den vollen bisherigen Umfang einschließlich Straßen, Flüssen und Stadtbahn bestätigt. Die Anwendung startet mit einer Stadtauswahl und zeigt danach erst die Themen. Taipei/New Taipei bleiben als gemeinsame Region erhalten. Düsseldorf verwendet deutsche Originalnamen; Lernstände und Einstellungen müssen je Region getrennt bleiben. Ein Regionswechsel darf bestehende Lernstände nicht löschen. Straßen, die Gebietsgrenzen überschreiten, müssen in jeder betroffenen Auswahl auffindbar sein. Die Quelle darf weder fehlende Klassifizierungen noch einen fehlenden aktuellen amtlichen Abgleich verschleiern. Die konkreten Anforderungen und Datenquellen stehen in REGIONEN.md. Seit 0.10 sind sechs Flüsse und getrennt schaltbare U-Bahn-, S-Bahn-, Straßenbahn- und SkyTrain-Ebenen aus öffentlichen Archiven eingebunden. Die schematische Verbindung von Haltestellen wird ausdrücklich erläutert.


## Düsseldorfer Quiz-Auswahl nach Stadtteilnamen · 0.11

Nach aktualisiertem Nutzerwunsch wird Düsseldorf über die 50 Stadtteilnamen wie Eller oder Wersten ausgewählt, ohne nummerierte Stadtbezirke als Quiz-Optionen. Die Auswahl über der Karte und die alphabetische Mehrfachauswahl verwenden dieselben Stadtteile; Straßen- und Flussauswahl folgen dieser Eingrenzung. Alte Bezirks-Auswahlen werden auf ihre Stadtteile übertragen, vorhandene Ergebnisse bleiben erhalten. Taipei behält die bisherige Stadtauswahl.

## Straßen in Zehner-Leveln · 0.12

Für jeden Stadtteil/Bezirk, jede Stadt und ausgewählte Gebietskombinationen beginnt Straßenlernen mit zehn langen ganzen Straßen. Jedes weitere Level enthält zehn neue Straßen; der letzte Rest darf kleiner sein. Maßgeblich ist die ungefähre Länge im gewählten Gebiet, nicht die Summe paralleler Fahrbahnen oder eine erfundene Straßenklasse. Die Einteilung darf durch freie Suche und Einzelauswahl nicht wandern. Alle Straßen des jeweiligen Bestands müssen über die Level erreichbar sein. Frühere Level sind erneut wählbar und optional zusätzlich mitübbar. Level-Positionen werden je Gebiet und Region gespeichert, gesichert und wiederhergestellt. Der Lernstand zeigt bereits richtig beantwortete Straßen; der Rundenabschluss bietet einen direkten Übergang zum nächsten Level. Bestehende freie Auswahl, Kartenquiz, Touch-Bedienung und lokale Offline-Nutzung bleiben erhalten. Umsetzungsdetails und Grenzen: STREET_LEVELS.md.
