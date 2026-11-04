/* Region selection and local, on-demand data loading. No external runtime services. */
(() => {
  "use strict";
  const t = window.I18n.t;
  const params = new URLSearchParams(location.search);
  const id = params.get("region");
  const $ = id => document.getElementById(id);
  const regions = {
    taipei: { id: "taipei", name: "Taipei & New Taipei", storagePrefix: "taipei-kennen", language: "zh-Hant", files: ["data/districts.js", "data/metro.js", "data/rivers.js", "data/streets.js", "data/street-parents.js", "data/levels-taipei.js"] },
    duesseldorf: { id: "duesseldorf", name: "Düsseldorf", storagePrefix: "duesseldorf-kennen", language: "de", files: ["data/duesseldorf.js", "data/levels-duesseldorf.js"] }
  };
  const region = regions[id];
  document.body.dataset.region = region?.id || "selection";
  $("region-view").hidden = Boolean(region);
  $("home-view").hidden = true;
  $("main-menu").hidden = !region;
  document.querySelector(".header-right").hidden = !region;
  if (!region) {
    document.title = t("m190");
    document.querySelector(".brand-mark").textContent = "⌖";
    document.querySelector(".brand-mark").lang = "de";
    $("page-heading").textContent = t("m191");
    document.querySelector(".intro-copy").textContent = t("m192");
    document.querySelector(".intro .eyebrow").textContent = t("m193");
    document.querySelector(".brand>span:last-child").textContent = t("m194");
    document.querySelector(".brand").setAttribute("aria-label", t("m195"));
    window.I18n.capture();
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
      script.src = path + "?v=0.14";
      script.onload = resolve;
      script.onerror = () => reject(new Error(t("fileError", path)));
      document.head.append(script);
    }
  });
  const loading = $("chapter-loading");
  loading.hidden = false;
  loading.showModal();
  $("ui-language-toggle").disabled = true;
  Promise.all(region.files.map(load)).then(async () => {
    if (region.id === "duesseldorf") {
      const data = window.DUESSELDORF_DATA;
      Object.assign(window, { TAIPEI_DATA: data.districts, TAIPEI_METRO: data.metro, TAIPEI_RIVERS: data.rivers,
        TAIPEI_STREETS: data.streets, TAIPEI_STREET_PARENTS: { features: [], replacedIds: [], aliases: {} } });
    }
    await load("region-ui.js");
    window.I18n.capture();
    await load("street-levels.js");
    await load("street-map.js");
    await load("app.js");
    loading.close(); loading.hidden = true;
    $("ui-language-toggle").disabled = false;
    document.body.dataset.ready = "true";
  }).catch(error => {
    loading.close(); loading.hidden = true;
    $("ui-language-toggle").disabled = false;
    $("region-error").hidden = false;
    $("region-error-message").textContent = error.message + t("m198");
    window.I18n.capture();
  });
})();
