# Prüfung der Straßen- und Menüerweiterung

Stand: 3. November 2026. Zielversion 0.7.

Der gemeinsame Integrationslauf mit 33 Prüfungen ist bestanden (434,287 s). Nach der abschließenden Ergänzung der zuvor vom neueren Innenstadt-Auszug nicht erfassten kleinen Straßen sind außerdem alle neun Straßen-/Menü-Browserprüfungen erneut bestanden (167,532 s), ebenso die auf sechs erweiterten Datenprüfungen (1,149 s). Damit sind 28 unterschiedliche Browserprüfungen und sechs Datenprüfungen abgedeckt. Die isolierte Einzeldatei- und Paketprüfung folgt vor dem Abschlusscommit.

## Prüfumfang

- Alle 41 Bezirke, beide Städte, Flüsse und Metro bleiben nutzbar.
- Straßen-Erkundung, Lernkarten, Quiz, richtige/falsche Antwort, Fehlerwiederholung und Fortschritt.
- Stadt, Bezirke, Straßenklasse, Sections/Lanes/Alleys, Suche und einzelne Straßen.
- Zielnamen und zugängliche Kartennamen vor der Antwort verbergen; Orientierungsschalter geben keine Antworten ab.
- Ganze Straßeneinheiten per Maus hervorheben und wählen; Touch-Auswahl vor der Antwort bestätigen; an Kreuzungen zwischen nahen Verläufen wechseln.
- Touch-Zoom, Verschieben und abgebrochene Gesten geben keine versehentlichen Antworten ab.
- Menü, mobile Navigation, Einstellungen, Hilfe, Verlaufssicherung, Importvalidierung und ausdrückliche Importbestätigung.
- Alte Lernstände und Einstellungen, Weiterverwendung nach Neuladen und Fortschrittslöschung.
- Reproduzierbare Quellenarchive, Hashes, eindeutige Aufgabenidentitäten, Geometrien und tatsächliche Abdeckung aller 41 Bezirke.
- Keine externen Laufzeitabrufe und keine JavaScript-Fehler während der Browserprüfungen.

## Grenzen der Aussage

Browserprüfungen laufen in Chromium einschließlich mobiler Touch-Emulation. Es ist damit kein Test auf jedem echten Android-/iOS-Gerät belegt. Die Einzeldatei wird isoliert über einen lokalen Testserver ohne weitere App-Dateien geprüft; die verwaltete Browserumgebung schränkt direkte `file://`-Navigation ein.

Die Datenprüfungen belegen den enthaltenen Bestand und seine Zuordnung, keine heutige amtliche Vollständigkeit. Geometrien außerhalb des Zentrums stammen aus einer 2021 versionierten Quelle, ergänzt um einen Innenstadt-Auszug von 2026. Englische Namen stammen aus dokumentierten Referenzen beziehungsweise aus regelbasierten numerischen Adresszusätzen; 1.362 Einheiten haben keine englische Zuordnung und werden standardmäßig nicht abgefragt. Aktueller Originalabgleich und abschließende Rechteprüfung vor öffentlicher Veröffentlichung bleiben offen.
