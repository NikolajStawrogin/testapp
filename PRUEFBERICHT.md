# Prüfung der Straßen- und Menüerweiterung

## Aktueller Stand 0.11 · Düsseldorfer Stadtteil-Auswahl

Gebietsauswahl und Quiz verwenden die 50 alphabetisch sortierten Stadtteilnamen wie Eller oder Wersten. Nummerierte Stadtbezirke und die bisherige Ebenenauswahl erscheinen nicht mehr als Quiz-Auswahl. Die Liste erlaubt mehrere Stadtteile für eine Runde; Straßen und Flüsse werden nach den ausgewählten Stadtteilen gefiltert. Bisherige ausgewählte Stadtbezirke werden in ihre zugehörigen Stadtteile übertragen, historische Antworten bleiben erhalten. Die Daten enthalten weiterhin die alten Stadtbezirksgeometrien und Kennungen, damit vorhandene Lernstände lesbar bleiben.

Elf Düsseldorfer Browserprüfungen bestanden in 15,490 s. Ein weiterer Lauf mit elf Prüfungen für eine gemeinsame Eller-/Wersten-Runde, Datenzuordnung, Pages-Unterpfad und die Offline-Einzeldatei beider Regionen bestand in 26,614 s. Wegen eines überlappenden Tests sind damit 21 unterschiedliche Prüfungen abgedeckt. Keine JavaScript-Fehler oder externen Laufzeitabrufe wurden festgestellt. Syntaxprüfung und `git diff --check` bestanden.

Die folgenden Abschnitte dokumentieren die früheren Versionen.

---

## Aktueller Stand 0.10 · Düsseldorf mit Flüssen und Bahnlinien

Die zuvor fehlenden Ebenen sind über andere öffentlich archivierte Quellen umgesetzt. Ein Originalserver-Abruf oder eine weitere Netzwerkfreigabe ist für diesen Stand nicht nötig. Enthalten sind sechs OSM-Flüsse sowie 26 aus VRR-Haltefolgen abgeleitete Bahnlinien (zwölf U-Bahn-/Stadtbahnlinien, sechs S-Bahnlinien, sieben Straßenbahnlinien, SkyTrain). Die Bahnarten sind einzeln schaltbar und werden gespeichert. Die ausdrücklich schematische Darstellung verbindet belegte Haltestellen; exakte Gleiskurven und aktuelle Betriebsdaten werden nicht zugesagt. Flussflächen sind angenäherte Flächen um archivierte OSM-Mittellinien.

**Prüfungen:** 15 Düsseldorfer Daten-/Browserprüfungen bestanden in 14,289 s. Enthalten: Quell-Hashes, reale Haltestellen als Linienendpunkte, Flussquiz mit falscher Antwort und erfolgreicher Fehlerwiederholung, versteckte Namen, Touch-Auswahl, getrennte Bahnarten und Sicherungsregionen sowie Upgrade alter Lernstände ohne Fortschrittsverlust. Sechs gezielte bestehende Prüfungen für Pages-Unterpfad, Taipei-Metro, alte Lernstände, Fluss- und Straßenquiz bestanden in 92,640 s. Zwei zusätzliche Einzeldatei-Prüfungen für mobiles Düsseldorfer Flussquiz und mobiles Taipei-Straßenquiz bestanden isoliert und offline in 14,340 s. Damit sind 23 gezielte Prüfungen dieses Ausbaus abgeschlossen; ein erneuter vollständiger Lauf sämtlicher übriger unveränderter Tests wurde nicht behauptet.

Ein zusätzlicher gezielter Upgrade-Nachlauf bestand in 1,872 s; dabei bleibt auch eine ausdrücklich leere Gebietsauswahl erhalten. Die beiden Offline-Datengeneratoren erzeugen byteidentische Ergebnisse. Sie prüfen die SHA-256 der festgehaltenen Archive vor der Verarbeitung. Es gab in den Browserprüfungen keine JavaScript-Fehler und keine externen Laufzeitabrufe. JavaScript-Syntax und `git diff --check` bestanden. Die Quellen, ihre Grenzen und Lizenznachweise stehen in REGIONEN.md und data/duesseldorf/layers-source-manifest.json. Die bekannten Einschränkungen echter Gerätetests und direkter file://-Navigation gelten weiter.

Die folgenden Abschnitte dokumentieren frühere Zwischenstände. Dort erwähnte ausstehende Düsseldorfer Ebenen beschreiben den damaligen Stand und sind mit 0.10 erledigt.

---

Stand: 3. November 2026. Zielversion 0.7.

Der abschließende gemeinsame Lauf mit 36 Prüfungen ist bestanden (450,679 s): 29 Browserprüfungen und sieben Datenprüfungen. Nach der mobilen Sichtprüfung wurden Menübeschriftung und Aufgabenanzeige über der Karte verbessert; die vier betroffenen mobilen Bezirks-/Fluss-/Straßenprüfungen sind danach erneut bestanden (32,375 s und 41,734 s).

Die endgültige Browser-Einzeldatei wurde in einem isolierten Verzeichnis geprüft, das ausschließlich diese HTML-Datei enthielt. Alle drei zusätzlichen Prüfungen für ganze Straßen und Namensverdeckung, mobiles Straßenquiz sowie Lernstand-Export/Import sind bestanden (64,797 s). Der mobile Durchlauf war nach dem ersten Öffnen vollständig offline, einschließlich Zoom, Verschieben, Vorschau, Bestätigung, Rundenabschluss, Menü und Hilfe. JavaScript-Fehler und externe Laufzeitabrufe wurden nicht festgestellt. Die JavaScript-Syntaxprüfung und `git diff --check` sind ebenfalls bestanden.

Das lokale ZIP-Paket enthält nach Ergänzung der Pages-Anleitung, `.nojekyll` und der Unterpfadtests 46 Dateien einschließlich Einzeldatei, Quellenarchiven, Datenskripten und Tests. `tools/package_app.py` hat die CRC-Prüfung bestanden und jeden archivierten Inhalt bytegenau mit seiner Quelldatei verglichen. Die Browser-Einzeldatei und das vollständige Paket sind jeweils etwa 21 MB groß. Git-interne Dateien und temporäre Entwicklungswerkzeuge sind nicht enthalten.

## Git-Zwischenstände

- `ad9b634`: bisherige geprüfte Bezirks-/Fluss-/Metro-App gesichert und gepusht.
- `b6d4ac5`: reproduzierbare Straßenquellen und Abdeckungsprüfungen gepusht.
- `088a2db`: Straßenlernen, Quiz, Navigation, Einstellungen und Lernstand-Sicherung gepusht.
- `1ea96cf`: ganze Straßen aus Sections, Schutz vor verräterischen Untereinheitsnamen und verbesserte mobile Aufgabenanzeige gepusht.

Für den geprüften Funktionsstand ergaben lokales `git rev-parse HEAD` und entferntes `git ls-remote origin refs/heads/main` identisch `1ea96cffabd99272a10b2911ff35a270bf28f433`. `git status --short --branch` zeigte anschließend keine offenen Änderungen. Die abschließende Dokumentation ergänzt diesen Stand; Anwendungscode und Daten bleiben dabei unverändert.

## Prüfumfang

- Alle 41 Bezirke, beide Städte, Flüsse und Metro bleiben nutzbar.
- Straßen-Erkundung, Lernkarten, Quiz, richtige/falsche Antwort, Fehlerwiederholung und Fortschritt.
- Stadt, Bezirke, Straßenklasse, Sections/Lanes/Alleys, Suche und einzelne Straßen.
- Zielnamen und zugängliche Kartennamen vor der Antwort verbergen; Orientierungsschalter geben keine Antworten ab.
- Ganze Straßeneinheiten per Maus hervorheben und wählen; Touch-Auswahl vor der Antwort bestätigen; an Kreuzungen zwischen nahen Verläufen wechseln.
- Touch-Zoom, Verschieben und abgebrochene Gesten geben keine versehentlichen Antworten ab.
- Ganze Straßen werden aus ihren Sections gebildet und bleiben zusätzlich zu einzelnen Sections wählbar. Beschriftungen untergeordneter Gassen verraten die übergeordnete Lösung nicht. Auf dem Handy stehen Aufgabe, Lösung und Weiter-Schaltfläche direkt über der Karte.
- Menü, mobile Navigation, Einstellungen, Hilfe, Verlaufssicherung, Importvalidierung und ausdrückliche Importbestätigung.
- Alte Lernstände und Einstellungen, Weiterverwendung nach Neuladen und Fortschrittslöschung.
- Reproduzierbare Quellenarchive, Hashes, eindeutige Aufgabenidentitäten, Geometrien und tatsächliche Abdeckung aller 41 Bezirke.
- Keine externen Laufzeitabrufe und keine JavaScript-Fehler während der Browserprüfungen.

## Grenzen der Aussage

Ergänzung GitHub Pages: Die beiden neuen Prüfungen in `tests/test_pages.py` sind bestanden (10,483 s). Sie prüfen alle acht lokalen App-Ressourcen, eine vollständige Quizrunde mit gespeichertem Ergebnis und das Handy-Menü unter dem echten Projekt-Unterpfad `/testapp/`. Das öffentliche Repository ist lesbar. Die Aktivierung selbst ist noch nicht als erfolgreich bestätigt: Sowohl Lesen als auch Anlegen der Pages-Einstellung über die GitHub-API werden in der Ausführungsumgebung mit „Forbidden“ blockiert. Code-Pushes funktionieren; die einmalige Pages-Quellwahl muss deshalb über die Repository-Einstellungen erfolgen.

Browserprüfungen laufen in Chromium einschließlich mobiler Touch-Emulation. Es ist damit kein Test auf jedem echten Android-/iOS-Gerät belegt. Die Einzeldatei wird isoliert über einen lokalen Testserver ohne weitere App-Dateien geprüft; die verwaltete Browserumgebung schränkt direkte `file://`-Navigation ein.

Die Datenprüfungen belegen den enthaltenen Bestand und seine Zuordnung, keine heutige amtliche Vollständigkeit. Geometrien außerhalb des Zentrums stammen aus einer 2021 versionierten Quelle, ergänzt um einen Innenstadt-Auszug von 2026. Englische Namen stammen aus dokumentierten Referenzen beziehungsweise aus regelbasierten numerischen Adresszusätzen; 1.363 wählbare Einheiten haben keine englische Zuordnung und werden standardmäßig nicht abgefragt. Aktueller Originalabgleich und abschließende Rechteprüfung vor öffentlicher Veröffentlichung bleiben offen.

## Ergänzung 0.8 · Kartenbedienung und Darstellung

Die App besitzt nun eine kräftige Straßenlösung über den Orientierungsebenen, eine direkte Infobox auf der Karte, eine standardmäßig geschlossene Metro-Legende, eine sichtbare Ladeanzeige vor Themenwechseln und die große Gebietsauswahl über der Karte. Rechteckige SVG-Fokusrahmen entfallen; die Tastaturmarkierung folgt weiterhin dem Kartenobjekt. Bei falschen Antworten unterscheidet die Infobox zwischen Lösung und eigener Auswahl. Mobile Zoomtasten bleiben frei.

Die Straßenansicht verwendet einen räumlichen Index für spielbare und Hintergrundstraßen. Gesten transformieren die bestehende Karte sofort; der aufwendige Straßenaufbau wartet bis 120 ms nach der letzten Bewegung. Nur Straßenbeschriftungen werden während dieser kurzen Phase verborgen. Bezirksbeschriftungen bleiben auch während einer Bewegung sichtbar. Der Finger-Trefferradius beträgt 30 CSS-Pixel und wird in Kartenkoordinaten umgerechnet, damit er beim Hineinzoomen nicht schrumpft.

Prüfstand: Alle 38 bestehenden Prüfungen wurden ausgeführt. Die zuerst gefundenen vier Abweichungen wurden behoben beziehungsweise an die gewünschte asynchrone Bedienung angepasst und einzeln erfolgreich nachgeprüft: unabhängige Stadtbeschriftung, geschlossene Metro-Legende, Navigation mit Ladeanzeige und Straßenbeschriftungen nach Zoom-Ende. Die übrigen 34 Bestandsprüfungen bestanden im Gesamtlauf. Drei zusätzliche UX-Prüfungen prüfen Infobox und Fokus, Gebietsauswahl und Legende, Ladeanzeige, das Ausbleiben von Straßen-DOM-Aufbau während einer Zoomserie, die spätere Aktualisierung, Lösungsstärke und Finger-Trefferzone. Damit sind 41 unterschiedliche Prüfungen im Gesamt- und in gezielten Nachläufen abgedeckt. Desktop- und mobile Darstellung wurden zusätzlich anhand von Browser-Screenshots kontrolliert.

Die Leistungsprüfung belegt weniger Arbeit im Eingabepfad, keine garantierte Bildrate auf jedem Handy. Die Tests laufen in Chromium mit mobiler Touch-Emulation; ein echter Android-/iOS-Gerätetest steht aus. Datenbestand und Datenlizenzen sind unverändert.

Die exportierte Einzeldatei 0.8 bestand zusätzlich alle drei isolierten Browserprüfungen für ganze Straßen, mobiles Offline-Quiz und Lernstand-Export/Import (64,709 s). Das ZIP enthält 47 Dateien; CRC und bytegenaue Übereinstimmung mit den Quelldateien werden beim Paketbau geprüft. JavaScript-Syntaxprüfung und `git diff --check` bestanden.

## Düsseldorf und regionaler Einstieg · Zwischenstand 0.9

Der neue Einstieg trennt die Stadtauswahl von den Themen. Taipei/New Taipei bleiben eine Region. Düsseldorf besitzt 50 Stadtteile, zehn aus den Stadtteilen gebildete Stadtbezirke und 2.891 benannte Straßen- und Wegeeinheiten mit Abdeckung aller 50 Stadtteile. Regionale Daten werden bedarfsgerecht geladen. Einstellungen und Lernstände sind getrennt; alte Taipei-Sicherungen bleiben importierbar, werden aber in Düsseldorf zurückgewiesen. Die Quellen sind historisch und ausdrücklich kein aktuelles amtliches Straßenverzeichnis. Fehlende Straßenklassen bleiben als unbekannt erkennbar.

Fünf neue Düsseldorfer Browserprüfungen bestanden zunächst in 7,353 s: Einstieg und Datenabrufe, Gebietsebenen und Quiz, Straßenquiz und getrennte Lernstände, Import der falschen Region, mobile Oberfläche und Touch. Fünf zusätzliche Datenprüfungen kontrollieren Hierarchie, eindeutige Identitäten, Abdeckung und gebietsüberschreitende Königsallee, SHA-256 aller Quellkopien sowie die ausdrücklich fehlenden Fluss-/Stadtbahndaten. Ein gezielter Nachlauf einschließlich mobiler Touch-Markierung und Themennavigation bestand mit sieben Prüfungen in 25,042 s. Die beiden Pages-Unterpfadprüfungen bestanden in 10,161 s.

Die exportierte Einzeldatei wurde in einem Verzeichnis ohne weitere App-Dateien geprüft: Mobile Straßenquiz funktionieren für Düsseldorf und Taipei bei nach dem Öffnen abgeschaltetem Netzwerk; es gab je Durchlauf nur den initialen HTML-Abruf und keine Skript-/Daten-Nachladeabrufe oder JavaScript-Fehler.

**Offener Teil des Nutzerauftrags:** Flüsse und Stadtbahn für Düsseldorf sind noch nicht umgesetzt und getestet, weil die Originalquellen in der laufenden Cloud-Umgebung per Netzwerkpolitik blockiert sind. Ein Entwurf mit den drei benötigten Domains ist gespeichert; das Konfigurationstool verlangt Veröffentlichung. Der vorbereitete Overpass-Kollektor ist syntaxgeprüft, sein Live-Abruf und die dadurch erzeugten Fluss- und Stadtbahndaten sind ausdrücklich ungeprüft. Deaktivierte Themen sind keine bestandenen Fluss-/Stadtbahn-Funktionstests. REGIONEN.md dokumentiert die genaue Fortsetzung. Der Regressionsabschluss ist unten dokumentiert.

Abschluss der Regression: Im ersten Langlauf wurden 14 bestehende Prüfungen erfolgreich abgeschlossen, bevor der Ausführungsprozess verloren ging; dieser Lauf besitzt deshalb keinen vollständigen Suite-Abschluss. Die übrigen 37 Prüfungen wurden anschließend als vollständiger Nachlauf ausgeführt: **37 bestanden, null Fehler, null Fehlschläge, null übersprungen**, 292,697 s. Damit wurden alle 51 unterschiedlichen Prüfungen des aktuellen Zwischenstands erfolgreich abgedeckt, einschließlich der zehn neuen Düsseldorfer Daten-/Browserprüfungen. Ein erneuter Datenaufbau erzeugte byteidentische Dateien. Der originale Stadtteilauszug wurde zusätzlich bytegenau gegen die gepinnte GitHub-Version geprüft. JavaScript-Syntax und `git diff --check` bestanden.

Das vollständige Zwischenstands-ZIP enthält 60 Dateien und wurde per CRC sowie bytegenau gegen sämtliche Quelldateien geprüft. Die direkte Einzeldatei-Navigation über `file://` wurde zusätzlich versucht, wird aber von der verwalteten Chromium-Richtlinie mit `ERR_BLOCKED_BY_ADMINISTRATOR` verhindert. Diese Navigation ist damit nicht funktional bestätigt. Die Einzeldatei selbst wurde isoliert über einen lokalen Testserver für beide Regionen geprüft; nach dem initialen Öffnen funktionieren die mobilen Straßenquiz vollständig ohne Netzwerk. Ein Test auf echten Android-/iOS-Geräten ist weiterhin nicht belegt.
