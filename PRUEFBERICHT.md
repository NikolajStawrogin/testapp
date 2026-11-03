# Prüfung der Straßen- und Menüerweiterung

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
