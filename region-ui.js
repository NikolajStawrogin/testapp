/* Localized presentation for the selected region; the learning engine stays shared. */
(() => {
  const region = window.APP_REGION;
  if (region.id !== "duesseldorf") return;
  const $ = id => document.getElementById(id);
  const data = window.DUESSELDORF_DATA;
  document.title = "Düsseldorf kennen · Straßen, Stadtteile und Flüsse lernen";
  document.querySelector('meta[name="description"]').content = "Lerne Düsseldorfer Straßen, 50 Stadtteile, 10 Stadtbezirke und Flüsse mit einer lokalen Lernkarte und Quiz.";
  document.querySelector(".brand>span:last-child").textContent = "Düsseldorf kennen.";
  document.querySelector(".brand").setAttribute("aria-label", "Düsseldorf kennen, Themenauswahl");
  document.querySelector(".brand-mark").textContent = "D";
  document.querySelector(".brand-mark").lang = "de";
  $("page-heading").textContent = "Düsseldorf wird vertrauter.";
  document.querySelector(".intro .eyebrow").textContent = "DEINE HEIMATSTADT BESSER KENNEN";
  document.querySelector(".intro-copy").textContent = "Straßen, Stadtteile, Stadtbezirke und Flüsse in Düsseldorf kennenlernen.";
  if (!data.rivers.features.length) {
    const card = document.querySelector('[data-start="rivers"]');
    card.disabled = true;
    card.querySelector("strong+span").textContent = "Daten werden noch ergänzt";
    $("include-rivers").disabled = true;
    $("show-rivers").disabled = true;
    $("show-river-labels").disabled = true;
  }
  $("transport-kind-settings").hidden = false;
  $("show-metro").nextElementSibling.textContent = "Bahnlinien anzeigen · schematisch";
  document.querySelector("#metro-legend summary").textContent = "U-Bahn, S-Bahn & Straßenbahn · Legende";
  if (!data.metro.lines.length) $("show-metro").disabled = true;
  const areaCard = document.querySelector('[data-start="districts"]');
  areaCard.querySelector("strong").textContent = "Stadtteile kennenlernen";
  areaCard.querySelector("strong+span").textContent = "50 Namen · von Angermund bis Wittlaer";
  areaCard.querySelector(".home-card-icon").textContent = "⌖";
  document.querySelector('[data-start="streets"] .home-card-icon').textContent = "↗";
  document.querySelector('[data-start="rivers"] .home-card-icon').textContent = "≈";
  if (data.rivers.features.length) document.querySelector('[data-start="rivers"] strong+span').textContent = data.rivers.features.map(f => f.nameZh).join(" · ");
  document.querySelector('[data-subject="districts"]').textContent = "Gebiete & Flüsse";
  document.querySelector('.subject.active strong').textContent = "Stadtteile";
  document.querySelector('.subject.active small').textContent = "50 Stadtteile · Eller, Wersten, Bilk und mehr";
  $("area-level-field").hidden = true;
  $("district-picker").setAttribute("aria-label", "Gebiete auswählen");
  $("district-picker").previousElementSibling.querySelector(".section-label").textContent = "03 / DEINE GEBIETE";
  $("city-scope").replaceChildren(new Option("Ganz Düsseldorf", "all"), ...data.districts.features.filter(feature => feature.level === "neighborhood").sort((a,b) => a.nameZh.localeCompare(b.nameZh,"de")).map(feature => new Option(feature.nameZh, feature.id)));
  $("language").replaceChildren(new Option("Deutsch · Originalnamen", "de"));
  $("language").disabled = true;
  const labelSettings = document.querySelector(".label-settings");
  labelSettings.replaceChildren();
  const legend = document.createElement("legend");
  legend.textContent = "Stadtteilnamen auf der Karte";
  labelSettings.append(legend);
  const namesLabel = document.createElement("label");
  namesLabel.className = "checkbox-row";
  const namesInput = document.createElement("input");
  namesInput.type = "checkbox"; namesInput.id = "show-neighborhood-labels";
  namesLabel.append(namesInput, document.createTextNode("Stadtteilnamen anzeigen"));
  labelSettings.append(namesLabel);
  for (const city of data.districts.cities) {
    const input = document.createElement("input");
    input.id = "show-labels-" + city.id;
    input.type = "checkbox"; input.hidden = true;
    labelSettings.append(input);
  }
  const units = document.querySelector('[name="street-unit"]').closest("fieldset");
  units.hidden = true;
  const bilingual = $("only-bilingual");
  if (bilingual) bilingual.closest("label").hidden = true;
  const categoryGroup = document.querySelector('[name="street-category"]').closest("fieldset");
  const label = document.createElement("label");
  const input = document.createElement("input");
  input.name = "street-category"; input.type = "checkbox"; input.value = "unclassified";
  label.append(input, document.createTextNode("Ohne Straßenklasse"));
  categoryGroup.append(label);
  $("taipei-map").setAttribute("aria-label", "Zoombare Lernkarte von Düsseldorf. Stadtteile, Stadtbezirke, Straßen und Flüsse mit Maus, Tastatur oder Touch auswählen.");
  document.querySelector('.map-panel').setAttribute("aria-label", "Interaktive Karte von Düsseldorf");
  document.querySelector('.metro-legend-note').textContent = data.metro.note;
  document.querySelector('.map-footer>span').replaceChildren(document.createTextNode("Karte/Flüsse: © OSM · ODbL · Bahn: VRR (Haltefolgen) · "), Object.assign(document.createElement("span"), { id:"river-credit" }), Object.assign(document.createElement("span"), { id:"metro-credit" }), Object.assign(document.createElement("span"), { id:"street-credit" }));
  const sources = $("sources-dialog");
  for (const node of [...sources.children].slice(1)) node.remove();
  const p = document.createElement("p");
  p.textContent = data.note;
  sources.append(p);
  for (const source of data.sources) {
    const h = document.createElement("h3"); h.textContent = source.name;
    const paragraph = document.createElement("p"); paragraph.textContent = source.note + " ";
    const link = document.createElement("a");link.href=source.url;link.target="_blank";link.rel="noopener noreferrer";link.textContent="Quelle und Datenstand";
    paragraph.append(link);sources.append(h,paragraph);
  }
  const privacy = document.createElement("p");
  privacy.textContent = "Alle Kartendaten werden gemeinsam mit der App ausgeliefert. Kein Karten-API-Schlüssel, keine Tracker und keine externen Laufzeitdienste. Lernstand und Einstellungen sind pro Stadt getrennt im lokalen Browserspeicher. Quellenlinks öffnen sich erst beim Anklicken. Die Online-Auslieferung erfolgt gegebenenfalls über GitHub Pages.";
  sources.append(privacy);
  const help = $("help-dialog");
  for (const node of [...help.children].slice(1)) node.remove();
  const text = document.createElement("p");
  text.textContent = "Wähle zuerst ein Thema. Wähle oben einen Stadtteil wie Eller oder Wersten oder wähle in der Liste mehrere Stadtteile für eine gemeinsame Runde. Geübt werden die Stadtteilnamen. Auch das Straßenquiz lässt sich so auf deine Stadtteile eingrenzen. Straßen werden als ganze benannte Verläufe gespielt. Bahnarten lassen sich in den Einstellungen einzeln einblenden. Ihre Linien sind schematische Verbindungen zwischen VRR-Haltestellen. Rhein und weitere enthaltene Flüsse lassen sich einzeln mitüben; für reine Flussrunden hebe die Gebietsauswahl auf. Karte ziehen und mit Rad oder zwei Fingern zoomen. Eine Finger-Auswahl wird vor der Quizantwort bestätigt; an Kreuzungen hilft Andere Straße. Lernkarten werden nicht bewertet. Unter Fortschritt kannst du den Lernstand sichern und wieder einlesen; Sicherungen gelten jeweils für die ausgewählte Stadt. Über Stadt wechseln kehrst du zur Stadtauswahl zurück.";
  help.append(text);
  // Preserve the shared sources-button listener installed by app.js.
  const button = document.createElement("button");button.id="help-sources";button.className="button button-secondary";button.textContent="Datenquellen";help.append(button);
})();
