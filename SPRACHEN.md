# Oberflächensprachen · 0.14

Die gesamte Bedienoberfläche ist in Englisch und traditionellem Chinesisch verfügbar. Auf einem ersten Besuch ohne gespeicherte Oberflächensprache startet die App auf traditionellem Chinesisch (`zh-Hant`), unabhängig von der Browsersprache. Im Sprachmenü heißt diese Sprache **國語**, in der englischen Oberfläche **Mandarin**. Es gibt keine vereinfachte Schriftvariante.

Oben rechts ist auf jeder Seite ein Globus mit Sprachkürzel sichtbar, auch vor der Stadtauswahl und auf dem Handy. Öffnen und Sprache wählen; die Änderung gilt sofort. Die Auswahl wird unter `stadt-kennen.ui-language.v1` im lokalen Browserspeicher gespeichert, gemeinsam für beide Lernregionen. Spätere Besuche und Stadtwechsel behalten sie. Falls der Browser keinen Speicher erlaubt, bleibt die Umschaltung für die aktuelle Seite nutzbar; beim nächsten Öffnen gilt wieder der Erststart.

Vor der aufwendigen Aktualisierung erscheint ein modaler Ladehinweis, auch über geöffneten Kartenoptionen. Die Anzeige wird vor der Kartenarbeit gezeichnet und nach Abschluss wieder geschlossen.

Menüs, Level-Auswahl, Quizanweisungen und Rückmeldungen, Kartenbedienung, Hilfe, Quellenhinweise, Lernstand und Fehlermeldungen werden übersetzt. Umschalten benötigt kein Neuladen und beendet keine Quizrunde. Ziel, abgegebene Antworten, Gebiet, Level und Zoom bleiben erhalten. Die Sprache selbst wird weder als Antwort gewertet noch in den Lernstand geschrieben.

## Sprache der Ortsnamen

Die Oberflächensprache ist von „地名顯示語言 / Place-name language“ getrennt. Für Taipei/New Taipei bleiben 國語/Mandarin, Englisch und beide Namensformen wählbar. Traditionelle Ortsnamen und belegte englische Schreibweisen bleiben in den unveränderten Daten. Fehlende englische Namen werden nicht erfunden. Düsseldorfer Straßen und Stadtteile behalten ihre deutschen Originalnamen auch in einer englischen oder chinesischen Oberfläche; es werden keine ungesicherten Übersetzungen eingeführt.

Bisherige Einstellungen, Antworten, Level-Positionen und Sicherungsformate bleiben lesbar. Die bestehende Einstellung `language` betrifft weiterhin ausschließlich Ortsnamen; sie wird nicht als Oberflächensprache umgedeutet. Lernstände bleiben je Region getrennt. Die gemeinsame Spracheinstellung wird beim Löschen eines regionalen Lernstands nicht gelöscht.

## Entwicklung und Offline-Version

`i18n.js` enthält den vollständigen lokalen Katalog und die Umschaltung. Ein Eintrag enthält Referenztext, englische Übersetzung und traditionelle Übersetzung. Platzhalter wie `{0}` werden als Text eingefügt. Keine Übersetzungsdienste, externen Schriftarten, Cookies oder neuen Laufzeitpakete werden verwendet.

Statische HTML-Texte und barrierefreie Beschriftungen verwenden `data-i18n` und `data-i18n-aria-label`/`title`/`placeholder`/`content`. Durch die Regionsanpassung erzeugte statische Texte werden einmalig vor dem Kartenaufbau gebunden. Dynamische Texte verwenden `I18n.t(key, ...values)` und werden beim Sprachwechsel neu gerendert. Es gibt keinen MutationObserver über der umfangreichen SVG-Karte. Neue dynamisch erstellte Auswahllisten müssen ihre Sprache bei einer zwischengespeicherten Darstellung berücksichtigen.

Die Browser-Einzeldatei bindet Übersetzungen vor dem Bootstrap-Skript ein. Sie verwendet denselben Katalog und dieselbe Umschaltung wie die Website. Die Tests prüfen Erststart, Sprachbezeichnungen, Tastaturbedienung, Sprachwechsel in laufenden Quizrunden, Trennung von Ortsnamen, Erhalt gespeicherter Fortschritte, mobile Darstellung, Quellenhinweise, blockierten Speicher und eine isoliert ausgelieferte Einzeldatei nach dem Öffnen ohne Netzwerk.
