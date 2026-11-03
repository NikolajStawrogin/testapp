/* Region selection and local, on-demand data loading. No external runtime services. */
(() => {
  "use strict";
  const params = new URLSearchParams(location.search);
  const id = params.get("region");
  const $ = id => document.getElementById(id);
  const regions = {
    taipei: { id: "taipei", name: "Taipei & New Taipei", storagePrefix: "taipei-kennen", language: "zh-Hant", files: ["data/districts.js", "data/metro.js", "data/rivers.js", "data/streets.js", "data/street-parents.js"] },
    duesseldorf: { id: "duesseldorf", name: "Düsseldorf", storagePrefix: "duesseldorf-kennen", language: "de", files: ["data/duesseldorf.js"] }
  };
  const region = regions[id];
  document.body.dataset.region = region?.id || "selection";
  $("region-view").hidden = Boolean(region);
  $("home-view").hidden = true;
  $("main-menu").hidden = !region;
  document.querySelector(".header-right").hidden = !region;
  if (!region) {
    document.title = "Stadt kennen · Wähle deine Stadt";
    document.querySelector(".brand-mark").textContent = "⌖";
    document.querySelector(".brand-mark").lang = "de";
    $("page-heading").textContent = "Welche Stadt möchtest du kennenlernen?";
    document.querySelector(".intro-copy").textContent = "Wähle deine Stadt. Danach entscheidest du dich für Straßen, Gebiete oder Flüsse.";
    document.querySelector(".intro .eyebrow").textContent = "DEIN ORTSSINN. DEINE STADT.";
    document.querySelector(".brand>span:last-child").textContent = "Stadt kennen.";
    document.querySelector(".brand").setAttribute("aria-label", "Stadt kennen, Stadtauswahl");
    return;
  }
  window.APP_REGION = region;
  window.APP_OPEN_TOPICS = location.hash === "#topics";
  if (window.APP_OPEN_TOPICS) { try { history.replaceState(null, "", location.pathname + location.search); } catch { /* Some file browsers restrict history edits. */ } }
  const load = path => new Promise((resolve, reject) => {
    const script = document.createElement("script");
    if (window.APP_EMBEDDED?.[path] !== undefined) {
      script.textContent = window.APP_EMBEDDED[path];
      document.body.append(script);
      resolve();
    } else {
      script.src = path + "?v=0.10";
      script.onload = resolve;
      script.onerror = () => reject(new Error("Die Datei „" + path + "“ konnte nicht geladen werden."));
      document.head.append(script);
    }
  });
  const loading = $("chapter-loading");
  loading.hidden = false;
  Promise.all(region.files.map(load)).then(async () => {
    if (region.id === "duesseldorf") {
      const data = window.DUESSELDORF_DATA;
      Object.assign(window, { TAIPEI_DATA: data.districts, TAIPEI_METRO: data.metro, TAIPEI_RIVERS: data.rivers,
        TAIPEI_STREETS: data.streets, TAIPEI_STREET_PARENTS: { features: [], replacedIds: [], aliases: {} } });
    }
    await load("region-ui.js");
    await load("street-map.js");
    await load("app.js");
    loading.hidden = true;
    document.body.dataset.ready = "true";
  }).catch(error => {
    loading.hidden = true;
    $("region-error").hidden = false;
    $("region-error-message").textContent = error.message + " Bitte lade die Seite neu oder wähle eine andere Stadt.";
  });
})();
