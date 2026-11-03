# App kostenlos mit Freunden teilen

Die Veröffentlichung über GitHub Pages wurde vom Repository-Inhaber beauftragt. Die App ist statisch: Freunde brauchen weder GitHub-Konto noch Installation oder Karten-API-Schlüssel. Ihr Fortschritt bleibt jeweils in ihrem eigenen Browser.

Vorgesehene Website: **https://nikolajstawrogin.github.io/testapp/**

## Einmalige GitHub-Einstellung

1. [Repository-Einstellungen → Pages](https://github.com/NikolajStawrogin/testapp/settings/pages) als Repository-Inhaber öffnen.
2. Unter **Build and deployment → Source** die Option **Deploy from a branch** wählen.
3. Als Branch **main**, als Ordner **/ (root)** wählen und **Save** anklicken.

Die Datei `.nojekyll` verhindert eine unnötige Jekyll-Verarbeitung. GitHub veröffentlicht die vorhandene `index.html` zusammen mit den lokalen Skripten, Styles und Kartendaten. Nachfolgende Pushes auf `main` werden automatisch übernommen. Für diesen Weg ist kein zusätzliches Workflow-Skript und kein persönlicher Zugriffsschlüssel erforderlich.

Nach dem ersten Speichern kann die Bereitstellung einige Minuten dauern. Den Erfolg zeigt GitHub in der Pages-Einstellung beziehungsweise unter **Actions → pages build and deployment**. Die Website ist erst nach erfolgreicher Bereitstellung aktiv; ein Repository-Push allein aktiviert Pages nicht.

## Kosten und Datenschutz

Das Repository ist öffentlich. GitHub Pages kann hierfür mit der bereitgestellten `github.io`-Adresse kostenlos genutzt werden. Es wird keine eigene Domain gekauft, kein Server gemietet und kein kostenpflichtiger Kartenanbieter eingerichtet.

Die App verwendet keine Anmeldung, Geolokalisierung oder Analysetracker. Die App-Dateien werden von GitHub Pages ausgeliefert; dabei gelten auch GitHubs Hosting- und Datenschutzbedingungen. Lernstände werden nicht an andere Spieler übertragen. Ein Wechsel von einer lokalen Adresse zur Website übernimmt den bisherigen Lernstand nicht automatisch; dafür stehen Export und Import im Menü „Fortschritt“ bereit.

## Quellen und Stand

Die Website verwendet dieselben dokumentierten Kartendaten wie die lokale App. Quellenangaben bleiben in der Karte und im Quellen-Dialog erhalten. Herkunft, ODbL-Bedingungen, ältere Datenstände und noch offene Primärquellen-/Namensprüfungen stehen in `THIRD_PARTY_NOTICES.md`, `OFFIZIELLE_NAMEN.md` und `data/*-SOURCE.md`. Es wird keine aktuelle amtliche Vollständigkeit oder Verifikation aller englischen Namen zugesagt.

## Technische Prüfung

`python -m unittest discover -s tests -p test_pages.py -v` prüft die Website unter dem Projekt-Unterpfad `/testapp/`, sämtliche verlinkten App-Dateien sowie eine Quizrunde und die mobile Navigation. Zur Aktivierung selbst ist ein GitHub-Zugriff mit Repository-Einstellungsrechten erforderlich.
