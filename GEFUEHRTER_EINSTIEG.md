# Geführter Einstieg und Spielansicht · 0.14

Nach der Stadtauswahl bereitet der Spieler eine Runde in fünf Schritten vor:

1. **Thema:** Gebiete, Straßen oder Flüsse. Ein Themenklick auf der Startseite beantwortet diesen Schritt bereits und öffnet direkt die Gebietsauswahl. Über „Zurück“ lässt sich das Thema ändern.
2. **Gebiet:** ganze Stadt beziehungsweise Taipei/New Taipei, ein einzelner Stadtteil oder mehrere ausgewählte Gebiete. Die lange Liste liegt in einer aufklappbaren Auswahl. Für reine Flussrunden werden keine Gebietsfragen hinzugefügt, auch nach einem Wechsel des Gebiets. Gebiete können auf Wunsch mit Flüssen kombiniert werden.
3. **Lernweise:** Entdecken, Lernkarten oder Quiz. Bei Straßen zusätzlich Level, Wiederholung beziehungsweise freie Auswahl mit den bisherigen Filtern. Die Straßenliste ist bei Leveln als Vorschau aufklappbar; in der freien Auswahl zugänglich. Die Zahl der Quizaufgaben ist separat wählbar.
4. **Kartenhilfen:** Sprache der Ortsnamen, Gebiets-, Straßen- und Flussnamen sowie Bahn- und Flussebenen. Im Straßen-Levelquiz werden Straßennamen vor der Antwort verborgen; eingeschaltete Namen erscheinen bei der Auflösung. Die Vorbereitung erläutert das ausdrücklich.
5. **Bestätigung:** Zusammenfassung mit gezielten „Ändern“-Knöpfen und dem Startknopf. Bei einer leeren Gebietsauswahl oder einer Auswahl ohne passende Aufgaben bleibt der nächste Schritt gesperrt und ein Hinweis erklärt den Grund.

Vor dem endgültigen Start erscheint **keine Karte**. Frühere Einstellungen werden als Vorschläge übernommen. Sie überspringen die Vorbereitung nicht, auch nicht nach einem Neuladen. Die umfangreiche Straßen-Kartenebene wird erst beim Spielstart aufgebaut.

## Spiel

Die Spielansicht ist eine eigene Bildschirmansicht mit einer Route `#play`. Sie besteht aus kompakter Aufgabenanzeige und einer großen Karte über die verfügbare Breite, ohne linke Einstellungsspalte. Die Hauptnavigation liegt in einem aufklappbaren Menü. „Kartenoptionen“ öffnet die Anzeigen-Einstellungen bei Bedarf in einem Dialog; „Runde anpassen“ kehrt zur Zusammenfassung zurück. Bereits abgegebene Antworten bleiben gespeichert. Eine vorzeitig verlassene Runde wird nicht als abgeschlossen gezählt.

Am Handy verwendet das Spiel die kompakte Aufgabenanzeige über der Karte. Die ausführliche Desktop-Aufgabenanzeige und die Vorbereitungsformulare bleiben ausgeblendet. Auswahlvorschau, Bestätigung von Finger-Eingaben, Zoomen, Verschieben und aufklappbare Bahnlegende bleiben erhalten. Ergebnisse erscheinen auf einer eigenen ruhigen Ansicht ohne Karte. Fehlerwiederholung und direkter Start des nächsten Straßen-Levels bleiben verfügbar.

Der Browser-Zurück-Knopf führt von der Karte zurück zur Vorbereitung. Eine bereits beendete Runde wird über „Vorwärts“ nicht versehentlich wiederhergestellt; stattdessen erscheint ihre aktuelle Vorbereitung. Alte Lernstände, Gebietsauswahlen und Straßen-Level bleiben lesbar.

## Sichtbare Ladezustände

Sowohl der Spielstart als auch ein Wechsel der Oberflächen- oder Ortsnamensprache zeigt zuerst einen Ladebildschirm. Beim Oberflächenwechsel erklärt dieser ausdrücklich, dass Karte und Beschriftungen aktualisiert werden und die Runde erhalten bleibt.

Der Browser erhält vor der aufwendigen synchronen Darstellung Gelegenheit zum Zeichnen. Erst danach beginnt die Aktualisierung. Die Anzeige ist ein modaler Statusdialog und erscheint auch über geöffneten Kartenoptionen. Doppelte Eingaben und Escape schließen den laufenden Status nicht. Nach Erfolg oder Fehler wird der Status aufgeräumt und die Bedienung wieder freigegeben. Es werden keine erfundenen Prozentwerte gezeigt.

Der Wechsel einer Sprache behält Frage, Antworten, Lernstand, Level und Zoom. Die Oberflächensprache und die separat einstellbare Sprache der Kartennamen bleiben voneinander unabhängig. Alle Schritte und Ladehinweise sind in Englisch und 國語 mit traditionellen Zeichen verfügbar. Es entstehen keine neuen externen Dienste oder laufenden Kosten.
