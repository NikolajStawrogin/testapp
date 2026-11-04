(() => {
  "use strict";
  const t = window.I18n.t;

  const REGION = window.APP_REGION || { id: "taipei", name: "Taipei & New Taipei", storagePrefix: "taipei-kennen", language: "zh-Hant" };
  const german = REGION.language === "de";
  const DATA = window.TAIPEI_DATA;
  const METRO = window.TAIPEI_METRO;
  const features = DATA.features;
  const rivers = window.TAIPEI_RIVERS.features;
  const streetParents = window.TAIPEI_STREET_PARENTS;
  const replacedStreetIds = new Set(streetParents.replacedIds);
  const streets = window.TAIPEI_STREETS.features.filter(feature => !replacedStreetIds.has(feature.id)).concat(streetParents.features);
  window.TAIPEI_STREETS.features = streets;
  const mapFeatures = [...features, ...rivers];
  const learningFeatures = [...mapFeatures, ...streets];
  const cities = DATA.cities;
  const byId = new Map(learningFeatures.map(feature => [feature.id, feature]));
  const streetProgressAliases = new Map();
  for (const [oldId, id] of Object.entries(streetParents.aliases)) {
    if (!streetProgressAliases.has(id)) streetProgressAliases.set(id, []);
    streetProgressAliases.get(id).push(oldId);
  }
  const cityById = new Map(cities.map(city => [city.id, city]));
  const $ = id => document.getElementById(id);
  const SVG_NS = "http://www.w3.org/2000/svg";
  const PROGRESS_KEY = `${REGION.storagePrefix}.progress.v1`;
  const SETTINGS_KEY = `${REGION.storagePrefix}.settings.v1`;
  const MIN_MAP_ZOOM = 0.5;
  const MAX_MAP_ZOOM = 12;
  const modes = ["explore", "cards", "quiz"];
  const languages = german ? ["de"] : ["both", "zh", "en"];
  let toastTimer;
  window.I18n.subscribe(() => { render(); renderProgress(); });

  function toast(message) {
    $("toast").textContent = message;
    $("toast").hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { $("toast").hidden = true; }, 5500);
  }

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key) || "null"); }
    catch { return null; }
  }

  function save(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; }
    catch {
      toast(t("m2"));
      return false;
    }
  }

  function count(value) {
    return Number.isSafeInteger(value) && value >= 0 ? value : 0;
  }

  function cleanStreetLevels(raw) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};
    return Object.fromEntries(Object.entries(raw).filter(([key,level]) => key.startsWith("whole-v1|") && key.length < 5000 && Number.isSafeInteger(level) && level > 0 && level <= 10000).slice(-300));
  }

  function cleanProgress(raw) {
    const result = { rounds: count(raw?.rounds), districts: {} };
    for (const feature of learningFeatures) {
      const rows = [feature.id, ...(streetProgressAliases.get(feature.id) || [])].map(id => raw?.districts?.[id]).filter(row => row && count(row.attempts));
      if (!rows.length) continue;
      result.districts[feature.id] = {
        attempts: Math.min(Number.MAX_SAFE_INTEGER, rows.reduce((total, row) => total + count(row.attempts), 0)),
        correct: Math.min(Number.MAX_SAFE_INTEGER, rows.reduce((total, row) => total + Math.min(count(row.correct), count(row.attempts)), 0))
      };
    }
    return result;
  }

  const savedSettings = load(SETTINGS_KEY);
  const upgradeLayers = german && savedSettings && savedSettings.datasetVersion < DATA.version;
  const legacyTaipei = features.filter(feature => feature.cityId === "taipei");
  const storedIds = Array.isArray(savedSettings?.selected) ? savedSettings.selected.filter(id => byId.has(id) && !byId.get(id).kind) : null;
  const expandLegacyAll = !german && savedSettings?.datasetVersion !== DATA.version && storedIds?.length === legacyTaipei.length
    && legacyTaipei.every(feature => storedIds.includes(feature.id));
  const initialLevel = "neighborhood";
  const migratedIds = german && storedIds ? [...new Set(storedIds.flatMap(id => {
    const feature = byId.get(id);
    return feature.level === "borough" ? features.filter(child => child.level === "neighborhood" && child.cityId === feature.cityId).map(child => child.id) : [id];
  }))] : storedIds;
  const initialIds = !migratedIds || expandLegacyAll ? features.filter(feature => !german || feature.level === initialLevel).map(feature => feature.id) : migratedIds;
  const storedScope = (german ? ["all", ...features.filter(feature => feature.level === "neighborhood").map(feature => feature.id)] : ["all", ...cities.map(city => city.id)]).includes(savedSettings?.scope) ? savedSettings.scope : null;
  const initialScope = expandLegacyAll ? "all" : storedScope || (initialIds.length && initialIds.every(id => byId.get(id).cityId === "taipei") ? "taipei" : "all");
  const state = {
    areaLevel: initialLevel,
    stage: "setup",
    view: !window.APP_OPEN_TOPICS && savedSettings && savedSettings.view !== "home" ? "practice" : "home",
    subject: savedSettings?.subject === "streets" ? "streets" : "districts",
    streetCategories: new Set(Array.isArray(savedSettings?.streetCategories) ? savedSettings.streetCategories.filter(value => ["major", "secondary", "local", "unclassified"].includes(value)) : german ? ["major", "secondary", "local", "unclassified"] : ["major", "secondary"]),
    streetUnits: new Set(Array.isArray(savedSettings?.streetUnits) ? savedSettings.streetUnits.filter(value => ["street", "section", "lane", "alley"].includes(value)) : ["street", "section"]),
    excludedStreets: new Set(Array.isArray(savedSettings?.excludedStreets) ? savedSettings.excludedStreets.map(id => streetParents.aliases[id] || id).filter(id => byId.get(id)?.kind === "street") : []),
    onlyBilingual: savedSettings?.onlyBilingual !== false,
    streetLabels: savedSettings?.streetLabels !== false,
    streetSearch: typeof savedSettings?.streetSearch === "string" ? savedSettings.streetSearch.slice(0, 120) : "",
    streetPath: savedSettings?.streetPath === "free" ? "free" : "levels",
    streetLevels: cleanStreetLevels(savedSettings?.streetLevels),
    levelReview: savedSettings?.levelReview === true,
    streetLimit: 40,
    hoveredStreet: null,
    pendingStreet: null,
    streetAlternatives: [],
    mode: modes.includes(savedSettings?.mode) ? savedSettings.mode : "explore",
    language: languages.includes(savedSettings?.language) ? savedSettings.language : german ? "de" : "both",
    labelsByCity: Object.fromEntries(cities.map(city => [city.id,
      typeof savedSettings?.labelsByCity?.[city.id] === "boolean"
        ? savedSettings.labelsByCity[city.id] : savedSettings?.labels !== false])),
    metro: Boolean(METRO.lines.length) && (upgradeLayers || savedSettings?.metro !== false),
    metroKinds: Object.fromEntries(["metro", "suburban", "tram", "other"].map(kind => [kind, savedSettings?.metroKinds?.[kind] !== false])),
    rivers: Boolean(rivers.length) && (upgradeLayers || savedSettings?.rivers !== false),
    riverLabels: savedSettings?.riverLabels !== false,
    includeRivers: Boolean(rivers.length) && savedSettings?.includeRivers === true,
    selectedRivers: new Set(Array.isArray(savedSettings?.selectedRivers) && !upgradeLayers
      ? savedSettings.selectedRivers.filter(id => rivers.some(river => river.id === id)) : rivers.map(river => river.id)),
    scope: initialScope,
    selected: new Set(initialIds.filter(id => initialScope === "all" || (german ? id === initialScope : byId.get(id).cityId === initialScope))),
    roundSize: savedSettings?.roundSize === "all" || savedSettings?.roundSize === 12 ? "all"
      : [5, 10].includes(savedSettings?.roundSize) ? savedSettings.roundSize : 10,
    inspected: null,
    round: null,
    progress: cleanProgress(load(PROGRESS_KEY))
  };
  let streetRevision = 0;
  let streetCandidateCache = null;
  let streetViewCache = null;
  let curriculumCache = null;
  let streetSelectionCache = null;

  function searchText(value) {
    return value.normalize("NFKC").toLowerCase().replaceAll("臺", "台").replace(/[\s.,’']/g, "");
  }

  function streetBaseCandidates() {
    const guided = state.streetPath === "levels";
    const englishRequired = !german && (state.language === "en" || (!guided && state.onlyBilingual));
    const key = [state.scope, [...state.selected].sort().join(), guided, [...state.streetCategories].sort().join(), [...state.streetUnits].sort().join(), englishRequired].join("|");
    if (streetCandidateCache?.key !== key) {
      streetCandidateCache = { key, features: streets.filter(feature => (state.scope === "all" || (german ? feature.districtIds.includes(state.scope) : feature.cityId === state.scope || feature.cityIds?.includes(state.scope)))
        && feature.districtIds.some(id => state.selected.has(id))
        && (guided ? feature.unit === "street" : state.streetCategories.has(feature.category) && state.streetUnits.has(feature.unit))
        && (!englishRequired || feature.nameEn)) };
    }
    return streetCandidateCache;
  }

  function streetLevelInfo() {
    if (state.streetPath !== "levels") return null;
    const base = streetBaseCandidates();
    const ids = [...state.selected];
    const areaKey = window.StreetLevels.areaKey(ids);
    if (curriculumCache?.key !== base.key) {
      const districts = features.filter(feature => !german || feature.level === "neighborhood");
      const groups = german ? [] : cities.map(city => ({ id: city.id, ids: districts.filter(feature => feature.cityId === city.id).map(feature => feature.id) }));
      curriculumCache = { key: base.key, ranked: window.StreetLevels.rank(base.features, window.STREET_LEVEL_DATA, ids, districts.map(feature => feature.id), groups) };
    }
    return { ...window.StreetLevels.slice(curriculumCache.ranked, state.streetLevels[areaKey] || 1, state.levelReview), areaKey, ranked: curriculumCache.ranked };
  }

  function streetCandidates() {
    const base = streetBaseCandidates();
    const level = streetLevelInfo();
    const key = base.key + "|" + (level ? `${level.level}|${state.levelReview}` : state.streetSearch);
    if (streetViewCache?.key !== key) {
      const query = searchText(state.streetSearch.trim());
      streetViewCache = { key, features: level ? level.active.map(row => row.feature) : base.features.filter(feature => !query || searchText(`${feature.nameZh} ${feature.nameEn}`).includes(query)) };
    }
    return streetViewCache;
  }

  function streetPool() {
    const candidates = streetCandidates();
    const key = candidates.key + "|" + streetRevision;
    if (streetSelectionCache?.key !== key) {
      const features = candidates.features.filter(feature => state.streetPath === "levels" || !state.excludedStreets.has(feature.id));
      streetSelectionCache = { key, features, ids: new Set(features.map(feature => feature.id)) };
    }
    return streetSelectionCache;
  }

  function learningAreaLabel() {
    if (state.selected.size === 1) return byId.get([...state.selected][0]).nameZh;
    if (state.selected.size === features.filter(feature => !german || feature.level === "neighborhood").length) return window.I18n.regionName(REGION);
    if (state.selected.size === scopeFeatures().length && state.scope !== "all") return german ? byId.get(state.scope).nameZh : cityName(cityById.get(state.scope));
    return t("m5", state.selected.size, areaWord(true));
  }

  function setStreetLevel(level) {
    const info = streetLevelInfo();
    if (!info?.total) return;
    state.streetLevels[info.areaKey] = Math.max(1, Math.min(info.total, level));
    state.streetLimit = 40; state.inspected = null;
    clearStreetPreview(); saveSettings(); render();
  }

  function renderStreetLevels() {
    const info = streetLevelInfo();
    $("street-learning-path").value = state.streetPath;
    $("street-level-controls").hidden = !info;
    $("street-category-filter").hidden = Boolean(info);
    $("street-unit-filter").hidden = Boolean(info) || german;
    $("street-bilingual-field").hidden = Boolean(info) || german;
    $("street-search-field").hidden = Boolean(info);
    $("street-select-all").hidden = Boolean(info);
    if (!info) return;
    const selector = $("street-level");
    const signature = info.areaKey + "|" + info.ranked.length + "|" + window.I18n.language();
    if (selector.dataset.signature !== signature) {
      selector.replaceChildren();
      for (let level = 1; level <= info.total; level++) {
        const start = (level - 1) * window.StreetLevels.SIZE + 1;
        selector.add(new Option(t("m6", level, start, Math.min(level * window.StreetLevels.SIZE, info.ranked.length)), String(level)));
      }
      selector.dataset.signature = signature;
    }
    selector.value = String(info.level); selector.disabled = !info.total;
    $("level-previous").disabled = info.level <= 1 || !info.total;
    $("level-next").disabled = info.level >= info.total;
    $("level-review").checked = state.levelReview;
    $("level-review").disabled = info.level === 1;
    $("street-level-summary").textContent = info.total ? t("m7", learningAreaLabel(), info.level, info.total, info.fresh.length, info.fresh.length === 1 ? t("m8") : t("m9"), state.levelReview && info.level > 1 ? t("m10", info.active.length) : "") : t("m11");
    const known = info.fresh.filter(row => state.progress.districts[row.feature.id]?.correct > 0).length;
    $("street-level-progress").textContent = info.total ? t("m12", known, info.fresh.length, info.fresh.length === 1 ? t("m8") : t("m9")) : "";
  }

  function maxMapZoom() { return state.subject === "streets" ? 96 : MAX_MAP_ZOOM; }

  function saveSettings() {
    save(SETTINGS_KEY, {
      areaLevel: state.areaLevel, view: state.view, subject: state.subject, streetCategories: [...state.streetCategories], streetUnits: [...state.streetUnits],
      streetPath: state.streetPath, streetLevels: state.streetLevels, levelReview: state.levelReview,
      excludedStreets: [...state.excludedStreets], onlyBilingual: state.onlyBilingual,
      streetLabels: state.streetLabels, streetSearch: state.streetSearch,
      mode: state.mode, language: state.language, labelsByCity: state.labelsByCity, metro: state.metro, metroKinds: state.metroKinds,
      rivers: state.rivers, riverLabels: state.riverLabels, includeRivers: state.includeRivers,
      selectedRivers: [...state.selectedRivers],
      selected: [...state.selected], roundSize: state.roundSize,
      scope: state.scope, datasetVersion: DATA.version
    });
  }

  function scopeFeatures() {
    return features.filter(feature => (!german || feature.level === state.areaLevel) && (state.scope === "all" || (german ? feature.id === state.scope : feature.cityId === state.scope)));
  }

  function scopeRivers() {
    return rivers.filter(river => state.scope === "all" || (german ? river.districtIds?.includes(state.scope) : river.cityIds.includes(state.scope)));
  }

  function selectedFeatures() {
    if (state.subject === "streets") return streetPool().features;
    return [...state.selected].map(id => byId.get(id)).concat(state.includeRivers
      ? scopeRivers().filter(river => state.selectedRivers.has(river.id)) : []);
  }

  function isPlayable(feature) {
    if (german && feature.level && feature.level !== state.areaLevel) return false;
    if (feature.kind === "street" && currentTarget()?.kind === "street" && feature.unit !== currentTarget().unit) return false;
    if (feature.kind === "street") return state.subject === "streets" && (streetPool().ids.has(feature.id)
      || (state.stage === "session" && state.round.ids.includes(feature.id)));
    if (state.subject === "streets") return false;
    return feature.kind === "river" ? state.includeRivers && state.selectedRivers.has(feature.id)
      && scopeRivers().some(river => river.id === feature.id) : state.selected.has(feature.id);
  }

  function currentTarget() {
    return state.stage === "session" ? byId.get(state.round.ids[state.round.position]) : null;
  }

  function riversVisible() {
    return state.rivers || currentTarget()?.kind === "river";
  }

  function featureContext(feature) {
    if (german) return feature.kind === "street" ? "Düsseldorf · " + feature.districtIds.filter(id => byId.get(id).level === "neighborhood").map(id => byId.get(id).nameZh).join(" / ") : feature.kind === "river" ? t("m15") : "Düsseldorf";
    if (feature.kind === "street") return cityName(cityById.get(feature.cityId)) + " · "
      + feature.districtIds.map(id => state.language === "en" ? byId.get(id).nameEn : byId.get(id).nameZh).join(" / ");
    return feature.kind === "river" ? t("m17") + feature.cityIds.map(id => cityName(cityById.get(id))).join(" / ")
      : cityName(cityById.get(feature.cityId));
  }

  function areaWord(plural = false) { return german ? state.areaLevel === "borough" ? plural ? t("m18") : t("m19") : plural ? t("m20") : t("m21") : plural ? t("m22") : t("m23"); }

  function roundLength(size) {
    return state.roundSize === "all" ? size : Math.min(state.roundSize, size);
  }

  function cityName(city) {
    if (german) return t(city.nameZh);
    if (state.language === "zh") return city.nameZh;
    if (state.language === "en") return city.nameEn;
    return `${city.nameZh} · ${city.nameEn}`;
  }

  function ringsOf(feature) {
    return feature.geometry.type === "MultiPolygon" ? feature.geometry.coordinates.flat() : feature.geometry.coordinates;
  }

  function extent(points) {
    return points.reduce((box, point) => [Math.min(box[0], point[0]), Math.min(box[1], point[1]), Math.max(box[2], point[0]), Math.max(box[3], point[1])], [Infinity, Infinity, -Infinity, -Infinity]);
  }

  function shuffled(ids) {
    const result = [...ids];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  function nameParts(feature) {
    if (german) return { main: feature.level === "borough" ? t(feature.nameZh) : feature.nameZh, secondary: "", lang: feature.level === "borough" ? window.I18n.language() : "de" };
    if (state.language === "en") return { main: feature.nameEn || feature.nameZh, secondary: "", lang: feature.nameEn ? "en" : "zh-Hant" };
    return {
      main: feature.nameZh,
      secondary: state.language === "both" ? feature.nameEn : "",
      lang: "zh-Hant"
    };
  }

  function readableName(feature) {
    const parts = nameParts(feature);
    return parts.secondary ? `${parts.main} · ${parts.secondary}` : parts.main;
  }

  class DistrictMap {
    constructor(onSelect) {
      this.svg = $("taipei-map");
      this.content = $("map-content");
      this.onSelect = onSelect;
      this.paths = new Map();
      this.labels = new Map();
      this.extents = new Map();
      this.anchors = new Map();
      this.zoom = 1;
      this.x = this.y = 0;
      this.suppressClickUntil = 0;
      this.pointer = null;
      this.touches = new Map();
      this.pinch = null;
      this.hadPinch = false;

      const mercator = ([lng, lat]) => [lng * Math.PI / 180, -Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360))];
      const points = features.flatMap(feature => ringsOf(feature).flatMap(ring => ring.map(mercator)));
      const [minX, minY, maxX, maxY] = extent(points);
      const scale = Math.min(870 / (maxX - minX), 680 / (maxY - minY));
      this.project = coordinate => {
        const [x, y] = mercator(coordinate);
        return [(x - (minX + maxX) / 2) * scale + 500, (y - (minY + maxY) / 2) * scale + 390];
      };

      const colors = ["#dce4c9", "#e4e8d3", "#d1dfc6", "#dfe5cb", "#d7dfbe", "#d2dcc4", "#e3e7cf", "#d1ddbd", "#dfe6cc", "#d9e4c4", "#cddbbf", "#d5e0c7"];
      const newTaipeiColors = ["#dce6e2", "#d2e0dc", "#e0e9e4", "#d7e4df", "#d5e1df", "#e2e9e1"];
      features.forEach((feature, index) => {
        const path = document.createElementNS(SVG_NS, "path");
        const rings = ringsOf(feature).map(ring => ring.map(point => this.project(point)));
        const d = rings.map(ring => ring.map((point, i) => `${i === 0 ? "M" : "L"}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join("") + "Z").join("");
        const anchor = this.project(feature.anchor);
        this.extents.set(feature.id, extent(rings.flat()));
        this.anchors.set(feature.id, anchor);
        path.setAttribute("d", d);
        const clipShape = document.createElementNS(SVG_NS, "path");
        clipShape.setAttribute("d", d);
        clipShape.setAttribute("clip-rule", "evenodd");
        $("metro-city-clip").append(clipShape);
        path.setAttribute("fill", (feature.cityId === "taipei" || german) ? colors[index % colors.length] : newTaipeiColors[index % newTaipeiColors.length]);
        path.setAttribute("fill-rule", "evenodd");
        path.setAttribute("class", "district-shape");
        path.setAttribute("data-id", feature.id);
        path.setAttribute("data-anchor-x", anchor[0]);
        path.setAttribute("data-anchor-y", anchor[1]);
        path.setAttribute("role", "button");
        path.setAttribute("tabindex", "0");
        path.addEventListener("keydown", event => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            this.onSelect(feature.id);
          }
        });
        $("district-shapes").append(path);
        this.paths.set(feature.id, path);

        const label = document.createElementNS(SVG_NS, "g");
        label.setAttribute("class", "district-label");
        label.setAttribute("data-id", feature.id);
        label.setAttribute("transform", `translate(${anchor[0]},${anchor[1]})`);
        const zh = document.createElementNS(SVG_NS, "text");
        zh.setAttribute("class", "zh");
        zh.setAttribute("lang", REGION.language);
        zh.textContent = feature.nameZh;
        const en = document.createElementNS(SVG_NS, "text");
        en.setAttribute("class", "en");
        en.setAttribute("lang", "en");
        en.textContent = feature.nameEn.replace(" Dist.", "");
        label.append(zh, en);
        $("district-labels").append(label);
        this.labels.set(feature.id, { group: label, zh, en });
      });

      this.drawRivers();
      this.drawMetro();

      this.svg.addEventListener("click", event => {
        if (performance.now() < this.suppressClickUntil) return;
        const id = this.selectionAt(event);
        if (id) this.onSelect(id);
      });
      $("map-stage").addEventListener("wheel", event => {
        if (!event.deltaY) return;
        event.preventDefault();
        const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? this.svg.clientHeight : 1;
        const delta = Math.max(-200, Math.min(200, event.deltaY * unit));
        this.zoomBy(Math.exp(-delta * 0.0025), this.svgPoint(event.clientX, event.clientY));
      }, { passive: false });
      this.svg.addEventListener("pointerdown", event => {
        if (event.pointerType === "touch") {
          this.touchStart(event);
          return;
        }
        if (event.button !== 0 || !event.isPrimary || this.touches.size) return;
        this.pointer = { id: event.pointerId, clientX: event.clientX, clientY: event.clientY, point: this.svgPoint(event.clientX, event.clientY), x: this.x, y: this.y, dragged: false };
      });
      this.svg.addEventListener("pointermove", event => {
        if (this.touches.has(event.pointerId)) {
          this.touchMove(event);
          return;
        }
        const pointer = this.pointer;
        if (!pointer && event.pointerType !== "touch" && state.subject === "streets") {
          hoverStreet(this.streets?.pick(event.clientX, event.clientY, false, state.hoveredStreet) || null);
        }
        if (!pointer || pointer.id !== event.pointerId) return;
        if (!pointer.dragged && Math.hypot(event.clientX - pointer.clientX, event.clientY - pointer.clientY) < 5) return;
        if (!pointer.dragged) {
          clearStreetPreview();
          pointer.dragged = true;
          this.svg.setPointerCapture(event.pointerId);
          this.svg.classList.add("dragging");
        }
        const point = this.svgPoint(event.clientX, event.clientY);
        this.x = pointer.x + point.x - pointer.point.x;
        this.y = pointer.y + point.y - pointer.point.y;
        this.applyTransform();
      });
      this.svg.addEventListener("pointerleave", () => { if (!this.pointer && !state.pendingStreet) hoverStreet(null); });
      const release = event => {
        if (this.touches.has(event.pointerId)) {
          this.touchEnd(event, event.type === "pointerup");
          return;
        }
        if (!this.pointer || this.pointer.id !== event.pointerId) return;
        if (this.pointer.dragged) this.suppressClickUntil = performance.now() + 180;
        this.pointer = null;
        this.svg.classList.remove("dragging");
        if (this.svg.hasPointerCapture(event.pointerId)) this.svg.releasePointerCapture(event.pointerId);
      };
      this.svg.addEventListener("pointerup", release);
      this.svg.addEventListener("pointercancel", release);
      this.svg.addEventListener("lostpointercapture", event => {
        if (this.touches.has(event.pointerId)) this.touchEnd(event, false);
        else if (this.pointer?.id === event.pointerId) {
          this.pointer = null;
          this.svg.classList.remove("dragging");
        }
      });
      this.svg.addEventListener("keydown", event => {
        if (event.ctrlKey || event.metaKey || event.altKey) return;
        if (["+", "=", "-", "0"].includes(event.key)) {
          event.preventDefault();
          if (event.key === "0") this.reset();
          else this.zoomBy(event.key === "-" ? 1 / 1.35 : 1.35);
        }
      });
      $("zoom-in").addEventListener("click", () => this.zoomBy(1.35));
      $("zoom-out").addEventListener("click", () => this.zoomBy(1 / 1.35));
      $("zoom-reset").addEventListener("click", () => this.reset());
      $("zoom-range").addEventListener("input", event => this.zoomBy(Number(event.target.value) / 100 / this.zoom));
      if (window.matchMedia("(pointer: coarse)").matches) {
        $("map-instruction").textContent = t("m31");
      }
      this.resizeObserver = new ResizeObserver(() => this.updateLabels());
      this.resizeObserver.observe(this.svg);
    }

    drawMetro() {
      const lines = new Map(METRO.lines.map(line => [line.id, line]));
      for (const feature of METRO.features) {
        const line = lines.get(feature.properties.line);
        const segments = feature.geometry.type === "MultiLineString"
          ? feature.geometry.coordinates : [feature.geometry.coordinates];
          const d = segments.map(segment => segment.map((coordinate, index) => {
            const point = this.project(coordinate);
            return `${index ? "L" : "M"}${point[0].toFixed(2)},${point[1].toFixed(2)}`;
          }).join("")).join("");
          const casing = document.createElementNS(SVG_NS, "path");
          casing.setAttribute("d", d);
          casing.setAttribute("class", "metro-casing");
          casing.dataset.kind = line.kind || "metro";
          $("metro-casings").append(casing);
          const path = document.createElementNS(SVG_NS, "path");
          path.setAttribute("d", d);
          path.setAttribute("class", "metro-line");
          path.dataset.kind = line.kind || "metro";
          path.setAttribute("stroke", line.color);
          path.setAttribute("data-line", line.id);
          path.setAttribute("data-relation", feature.properties.relation);
          $("metro-lines").append(path);
      }
    }

    drawRivers() {
      for (const feature of rivers) {
        const rings = ringsOf(feature).map(ring => ring.map(point => this.project(point)));
        const d = rings.map(ring => ring.map((point, index) => `${index ? "L" : "M"}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join("") + "Z").join("");
        const anchor = this.project(feature.anchor);
        this.extents.set(feature.id, extent(rings.flat()));
        this.anchors.set(feature.id, anchor);
        const group = document.createElementNS(SVG_NS, "g");
        group.classList.add("river-area");
        const path = document.createElementNS(SVG_NS, "path");
        path.setAttribute("class", "river-shape");
        path.setAttribute("d", d);
        path.setAttribute("fill-rule", "evenodd");
        path.dataset.id = feature.id;
        this.paths.set(feature.id, path);
        const hit = document.createElementNS(SVG_NS, "path");
        hit.setAttribute("class", "river-hit");
        hit.setAttribute("d", d);
        hit.setAttribute("fill-rule", "evenodd");
        hit.setAttribute("role", "button");
        hit.dataset.id = feature.id;
        hit.dataset.anchorX = anchor[0];
        hit.dataset.anchorY = anchor[1];
        hit.addEventListener("keydown", event => {
          if (event.key === "Enter" || event.key === " ") { event.preventDefault(); this.onSelect(feature.id); }
        });
        group.append(path, hit);
        $("river-layer").append(group);
        const label = document.createElementNS(SVG_NS, "g");
        label.setAttribute("class", "river-label");
        label.dataset.id = feature.id;
        label.setAttribute("transform", `translate(${anchor[0]},${anchor[1]})`);
        const zh = document.createElementNS(SVG_NS, "text");
        zh.setAttribute("class", "zh");
        zh.setAttribute("lang", REGION.language);
        zh.textContent = feature.nameZh;
        const en = document.createElementNS(SVG_NS, "text");
        en.setAttribute("class", "en");
        en.setAttribute("lang", "en");
        en.textContent = feature.nameEn;
        label.append(zh, en);
        $("district-labels").append(label);
        this.labels.set(feature.id, { group: label, zh, en, hit });
      }
    }

    ensureStreetLayer() {
      if (this.streets) return;
      this.streets = new window.TaipeiStreetLayer({ features: streets, background: window.TAIPEI_STREETS.background,
        project: this.project, root: $("street-layer"), labels: $("street-labels"), highlight: $("street-highlight-layer"),
        onSelect: this.onSelect, onHover: hoverStreet });
      for (const [id, item] of this.streets.items) { this.extents.set(id, item.bounds); this.anchors.set(id, item.anchor); }
    }

    renderStreets() {
      const visible = state.subject === "streets" && state.view === "practice";
      $("map-content").classList.toggle("has-street-level", visible && state.streetPath === "levels");
      $("street-map-hint").hidden = !visible;
      if (!visible && !this.streets) return;
      if (visible) this.ensureStreetLayer();
      const matrix = this.content.getScreenCTM();
      if (!matrix) return;
      const target = currentTarget();
      const revealed = state.stage === "session" && state.round.revealed;
      const answer = revealed ? state.round.answers.at(-1) : null;
      const pool = new Set(streetPool().ids);
      if (state.stage === "session") for (const id of state.round.ids) if (byId.get(id).kind === "street") pool.add(id);
      if (target?.kind === "street") for (const id of pool) if (byId.get(id).unit !== target.unit) pool.delete(id);
      this.streets.render({ visible, pool, zoom: this.zoom, matrix, viewport: this.svg.getBoundingClientRect(),
        language: state.language, focusPool: state.streetPath === "levels", names: state.streetLabels && !(state.streetPath === "levels" && state.stage === "session" && state.round.kind === "quiz" && !revealed), hiddenId: revealed ? null : target?.id,
        hiddenPrefix: revealed ? null : target?.nameZh,
        inSession: state.stage === "session", revealed,
        correctId: revealed && target?.kind === "street" ? target.id : null,
        wrongId: answer && !answer.correct ? answer.chosenId : null,
        highlightId: state.pendingStreet || state.hoveredStreet || (state.stage === "setup" && byId.get(state.inspected)?.kind === "street" ? state.inspected : null) });
    }

    touchStart(event) {
      event.preventDefault();
      this.touches.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY });
      this.svg.setPointerCapture(event.pointerId);
      if (this.touches.size >= 2) {
        this.hadPinch = true;
        this.pointer = null;
        this.beginPinch();
      } else {
        this.hadPinch = false;
        this.pointer = {
          id: event.pointerId, clientX: event.clientX, clientY: event.clientY,
          point: this.svgPoint(event.clientX, event.clientY), x: this.x, y: this.y,
          dragged: false, targetId: this.selectionAt(event)
        };
      }
    }

    beginPinch() {
      clearStreetPreview();
      const [first, second] = [...this.touches.values()];
      const center = this.svgPoint((first.clientX + second.clientX) / 2, (first.clientY + second.clientY) / 2);
      this.pinch = {
        distance: Math.max(1, Math.hypot(second.clientX - first.clientX, second.clientY - first.clientY)),
        zoom: this.zoom,
        point: { x: (center.x - this.x) / this.zoom, y: (center.y - this.y) / this.zoom }
      };
    }

    touchMove(event) {
      event.preventDefault();
      this.touches.set(event.pointerId, { clientX: event.clientX, clientY: event.clientY });
      if (this.touches.size >= 2) {
        const [first, second] = [...this.touches.values()];
        const center = this.svgPoint((first.clientX + second.clientX) / 2, (first.clientY + second.clientY) / 2);
        const distance = Math.hypot(second.clientX - first.clientX, second.clientY - first.clientY);
        this.zoom = Math.max(MIN_MAP_ZOOM, Math.min(maxMapZoom(), this.pinch.zoom * distance / this.pinch.distance));
        this.x = center.x - this.pinch.point.x * this.zoom;
        this.y = center.y - this.pinch.point.y * this.zoom;
        this.svg.classList.add("dragging");
        this.applyTransform();
      } else if (this.pointer?.id === event.pointerId) {
        const pointer = this.pointer;
        if (!pointer.dragged && Math.hypot(event.clientX - pointer.clientX, event.clientY - pointer.clientY) < 5) return;
      if (!pointer.dragged) clearStreetPreview();
        pointer.dragged = true;
        const point = this.svgPoint(event.clientX, event.clientY);
        this.x = pointer.x + point.x - pointer.point.x;
        this.y = pointer.y + point.y - pointer.point.y;
        this.svg.classList.add("dragging");
        this.applyTransform();
      }
    }

    touchEnd(event, allowTap) {
      const pointer = this.pointer;
      const tapId = allowTap && !this.hadPinch && this.touches.size === 1 && pointer && !pointer.dragged
        ? pointer.targetId : null;
      this.touches.delete(event.pointerId);
      this.suppressClickUntil = performance.now() + 500;
      if (this.svg.hasPointerCapture(event.pointerId)) this.svg.releasePointerCapture(event.pointerId);
      if (this.touches.size >= 2) {
        this.beginPinch();
      } else if (this.touches.size === 1) {
        const [id, touch] = [...this.touches.entries()][0];
        this.pinch = null;
        this.pointer = {
          id, clientX: touch.clientX, clientY: touch.clientY,
          point: this.svgPoint(touch.clientX, touch.clientY), x: this.x, y: this.y,
          dragged: true
        };
      } else {
        this.pinch = null;
        this.pointer = null;
        this.hadPinch = false;
        this.svg.classList.remove("dragging");
      }
      if (tapId) this.onSelect(tapId, { touch: true, alternatives: this.streets?.lastCandidates || [] });
    }

    svgPoint(clientX, clientY) {
      const point = this.svg.createSVGPoint();
      point.x = clientX;
      point.y = clientY;
      return point.matrixTransform(this.svg.getScreenCTM().inverse());
    }

    selectionAt(event) {
      if (state.subject === "streets") return this.streets?.pick(event.clientX, event.clientY, event.pointerType === "touch", event.pointerType === "touch" ? null : state.hoveredStreet) || null;
      if (riversVisible() && ((state.stage === "setup" && state.includeRivers) || currentTarget()?.kind === "river")) {
        const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(this.content.getScreenCTM().inverse());
        const containing = rivers.filter(river => this.paths.get(river.id).isPointInFill(point));
        // A wider touch target must never cover another river's actual water surface.
        if (containing.length) return containing.find(isPlayable)?.id || null;
      }
      return event.target.closest(".district-shape, .river-hit")?.dataset.id;
    }

    zoomBy(factor, point = { x: 500, y: 390 }) {
      const newZoom = Math.max(MIN_MAP_ZOOM, Math.min(maxMapZoom(), this.zoom * factor));
      const ratio = newZoom / this.zoom;
      this.x = point.x - (point.x - this.x) * ratio;
      this.y = point.y - (point.y - this.y) * ratio;
      this.zoom = newZoom;
      this.applyTransform();
    }

    applyTransform() {
      const clampOffset = (value, size, padding) => {
        const center = Math.max(0, size * (1 - this.zoom) / 2);
        const min = this.zoom < 1 ? center - padding : -size * (this.zoom - 1) - padding;
        return Math.max(min, Math.min(center + padding, value));
      };
      this.x = clampOffset(this.x, 1000, 180);
      this.y = clampOffset(this.y, 780, 140);
      this.content.setAttribute("transform", `translate(${this.x},${this.y}) scale(${this.zoom})`);
      $("zoom-in").disabled = this.zoom >= maxMapZoom();
      $("zoom-range").max = String(maxMapZoom() * 100);
      $("zoom-out").disabled = this.zoom <= MIN_MAP_ZOOM;
      $("zoom-range").value = String(Math.round(this.zoom * 100));
      $("zoom-level").textContent = `${Math.round(this.zoom * 100)} %`;
      this.updateLabels();
      // Keep gesture work small: transform existing vectors immediately, rebuild after input settles.
      this.svg.classList.add("is-moving");
      clearTimeout(this.settleTimer);
      this.settleTimer = setTimeout(() => {
        this.svg.classList.remove("is-moving");
        this.renderStreets();
      }, 120);
    }

    reset() {
      this.fit(state.subject === "streets" && state.selected.size ? [...state.selected].map(id => byId.get(id)) : scopeFeatures());
    }

    fit(selected) {
      if (!selected.length) return;
      if (selected.some(feature => feature.kind === "street")) this.ensureStreetLayer();
      const [minX, minY, maxX, maxY] = extent(selected.flatMap(feature => {
        const box = this.extents.get(feature.id);
        return [[box[0], box[1]], [box[2], box[3]]];
      }));
      const desired = Math.min(870 / (maxX - minX), 680 / (maxY - minY));
      this.zoom = Math.max(MIN_MAP_ZOOM, Math.min(maxMapZoom(), Math.abs(desired - 1) < 1e-8 ? 1 : desired));
      this.x = 500 - (minX + maxX) / 2 * this.zoom;
      this.y = 390 - (minY + maxY) / 2 * this.zoom;
      if (Math.abs(this.x) < 1e-8) this.x = 0;
      if (Math.abs(this.y) < 1e-8) this.y = 0;
      this.applyTransform();
    }

    updateLabels() {
      const matrix = this.svg.getScreenCTM();
      if (!matrix) return;
      const scale = Math.hypot(matrix.a, matrix.b) * this.zoom;
      const viewport = this.svg.getBoundingClientRect();
      const inSession = state.stage === "session";
      const target = inSession ? state.round.ids[state.round.position] : null;
      const revealed = inSession && state.round.revealed;
      const candidates = [];
      for (const feature of mapFeatures) {
        const label = this.labels.get(feature.id);
        label.group.style.display = "none";
        const enabled = feature.kind === "river" ? riversVisible() && state.riverLabels : state.labelsByCity[feature.cityId];
        if ((german && feature.level && feature.level !== state.areaLevel) || !enabled || (inSession && !revealed && feature.id === target)) continue;
        label.zh.style.display = state.language === "en" ? "none" : "";
        label.en.style.display = german || state.language === "zh" ? "none" : "";
        label.zh.style.fontSize = `${12 / scale}px`;
        label.en.style.fontSize = `${9 / scale}px`;
        label.group.style.strokeWidth = `${2.5 / scale}px`;
        label.zh.setAttribute("y", (state.language === "both" ? -3 : 4) / scale);
        label.en.setAttribute("y", (state.language === "both" ? 13 : 3) / scale);
        const width = Math.max(state.language !== "en" ? feature.nameZh.length * 13 : 0,
          state.language !== "zh" ? feature.nameEn.replace(" Dist.", "").length * 5.7 : 0) + 8;
        const height = state.language === "both" ? 29 : 19;
        const bounds = this.extents.get(feature.id);
        const important = feature.id === state.inspected || (revealed && feature.id === target);
        if (!important && ((bounds[2] - bounds[0]) * scale < width * .75 || (bounds[3] - bounds[1]) * scale < height * .75)) continue;
        const anchor = this.anchors.get(feature.id);
        const x = this.x + anchor[0] * this.zoom, y = this.y + anchor[1] * this.zoom;
        const cx = matrix.a * x + matrix.c * y + matrix.e;
        const cy = matrix.b * x + matrix.d * y + matrix.f;
        const box = [cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2];
        if (box[2] < viewport.left || box[0] > viewport.right || box[3] < viewport.top || box[1] > viewport.bottom) continue;
        candidates.push({ label, box, priority: important ? Infinity : (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) });
      }
      const occupied = [];
      for (const candidate of candidates.sort((a, b) => b.priority - a.priority)) {
        const box = candidate.box;
        if (occupied.some(other => box[0] < other[2] && box[2] > other[0] && box[1] < other[3] && box[3] > other[1])) continue;
        candidate.label.group.style.display = "";
        occupied.push(box);
      }
    }

    render() {
      $("metro-layer").style.display = state.metro ? "" : "none";
      for (const path of $("metro-layer").querySelectorAll("[data-kind]")) path.style.display = state.metroKinds[path.dataset.kind] ? "" : "none";
      $("river-layer").style.display = riversVisible() ? "" : "none";
      const inSession = state.stage === "session";
      const target = inSession ? state.round.ids[state.round.position] : null;
      const revealed = inSession && state.round.revealed;
      const answer = revealed ? state.round.answers.at(-1) : null;
      for (const feature of mapFeatures) {
        const isRiver = feature.kind === "river";
        const active = isPlayable(feature) && (!inSession || isRiver === (byId.get(target).kind === "river"));
        const path = this.paths.get(feature.id);
        path.parentElement === $("district-shapes") && (path.style.display = german && feature.level !== state.areaLevel ? "none" : "");
        path.classList.toggle("is-muted", !active && !isRiver);
        path.classList.toggle("is-selected", !inSession && feature.id === state.inspected);
        path.classList.toggle("is-correct", revealed && target === feature.id);
        path.classList.toggle("is-wrong", revealed && !answer.correct && answer.chosenId === feature.id);
        const control = isRiver ? this.labels.get(feature.id).hit : path;
        if (isRiver) control.style.pointerEvents = active && !revealed && riversVisible() ? "all" : "none";
        control.setAttribute("tabindex", active && !revealed && (!isRiver || riversVisible()) ? "0" : "-1");
        control.setAttribute("aria-disabled", String(!active || revealed));
        control.setAttribute("aria-label", inSession && !revealed ? isRiver ? t("m34") : t("m35") : readableName(feature));
      }
      this.updateLabels();
      this.renderStreets();
    }
  }

  const map = new DistrictMap(selectDistrict);

  function clearStreetPreview() {
    state.pendingStreet = null;
    state.streetAlternatives = [];
    state.hoveredStreet = null;
    $("street-confirmation").hidden = true;
    map.streets?.setHighlight(null);
  }

  function hoverStreet(id) {
    if (state.subject !== "streets" || state.pendingStreet || (state.stage === "session" && state.round.revealed)) return;
    state.hoveredStreet = id;
    map.streets?.setHighlight(id);
  }

  function renderStreetPicker() {
    if (state.subject !== "streets") return;
    renderStreetLevels();
    const level = streetLevelInfo();
    const available = streetCandidates().features;
    const selectedCount = streetPool().features.length;
    const picker = $("street-picker");
    const scroll = picker.scrollTop;
    const focused = picker.contains(document.activeElement) ? document.activeElement.value : null;
    picker.replaceChildren();
    for (const feature of available.slice(0, state.streetLimit)) {
      const label = document.createElement("label");
      label.className = "street-choice" + (level ? " is-level" : "");
      label.dataset.streetId = feature.id;
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = feature.id;
      input.checked = Boolean(level) || !state.excludedStreets.has(feature.id);
      input.hidden = Boolean(level); input.disabled = Boolean(level);
      input.setAttribute("aria-label", readableName(feature));
      input.addEventListener("change", () => {
        input.checked ? state.excludedStreets.delete(feature.id) : state.excludedStreets.add(feature.id);
        streetRevision++;
        saveSettings();
        render();
      });
      const names = document.createElement("span");
      const main = document.createElement("strong");
      main.lang = REGION.language;
      main.textContent = feature.nameZh;
      const english = document.createElement("small");
      english.lang = "en";
      english.textContent = feature.nameEn || t("m37");
      const context = document.createElement("small");
      context.className = "street-choice-context";
      context.textContent = feature.districtIds.filter(id => !german || byId.get(id).level === state.areaLevel).map(id => byId.get(id).nameZh).join(" · ");
      names.append(main, english, context);
      label.append(input);
      if (level) {
        const rank = document.createElement("span"); rank.className = "street-rank";
        rank.textContent = String(level.ranked.findIndex(row => row.feature.id === feature.id) + 1);
        label.append(rank);
      }
      label.append(names);
      picker.append(label);
    }
    picker.scrollTop = scroll;
    if (focused) picker.querySelector(`input[value="${focused}"]`)?.focus({ preventScroll: true });
    $("street-selection-count").textContent = t("m38", selectedCount.toLocaleString(window.I18n.locale()), available.length.toLocaleString(window.I18n.locale()));
    $("street-select-all").textContent = selectedCount === available.length && available.length ? t("m40") : t("m41");
    $("street-select-all").disabled = !available.length;
    $("street-more").hidden = available.length <= state.streetLimit;
    $("street-more").textContent = t("m42", Math.min(state.streetLimit, available.length), available.length);
    $("street-empty").hidden = available.length > 0;
    const missing = streets.filter(feature => feature.districtIds.some(id => state.selected.has(id)) && !feature.nameEn).length;
    $("street-data-note").textContent = german ? t(window.DUESSELDORF_DATA.note) : t("m43", missing.toLocaleString(window.I18n.locale()));
  }

  function buildPicker() {
    const root = $("district-picker");
    root.replaceChildren();
    if (german) {
      const grid = document.createElement("div");
      grid.className = "district-picker";
      for (const feature of scopeFeatures().sort((a,b) => a.nameZh.localeCompare(b.nameZh,"de"))) grid.append(createDistrictChoice(feature));
      root.append(grid);
      $("river-picker").replaceChildren(...scopeRivers().map(createDistrictChoice));
      return;
    }
    for (const city of cities) {
      const members = scopeFeatures().filter(feature => feature.cityId === city.id);
      if (!members.length) continue;
      const section = document.createElement("section");
      section.className = "district-group";
      const heading = document.createElement("h3");
      heading.className = "district-group-title";
      heading.dataset.city = city.id;
      const grid = document.createElement("div");
      grid.className = "district-picker";
      section.append(heading, grid);
      for (const feature of members) grid.append(createDistrictChoice(feature));
      root.append(section);
    }
    $("river-picker").replaceChildren(...scopeRivers().map(createDistrictChoice));
  }

  function createDistrictChoice(feature) {
      const label = document.createElement("label");
      label.className = "district-choice";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = feature.id;
      const selection = feature.kind === "river" ? state.selectedRivers : state.selected;
      input.checked = selection.has(feature.id);
      input.setAttribute("aria-label", `${feature.nameZh} · ${feature.nameEn}`);
      input.addEventListener("change", () => {
        const selection = feature.kind === "river" ? state.selectedRivers : state.selected;
        input.checked ? selection.add(feature.id) : selection.delete(feature.id);
        if (state.inspected && !isPlayable(byId.get(state.inspected))) state.inspected = null;
        saveSettings();
        render();
      });
      const zh = document.createElement("strong");
      zh.lang = REGION.language;
      zh.textContent = feature.nameZh;
      const en = document.createElement("small");
      en.lang = "en";
      en.textContent = feature.nameEn.replace(" Dist.", "");
      label.append(input, zh, en);
      return label;
  }

  function renderDetail(feature, title, description) {
    $("map-detail").hidden = !feature;
    const content = $("map-detail").lastElementChild;
    const strong = document.createElement("strong");
    const paragraph = document.createElement("p");
    strong.textContent = title || (feature ? readableName(feature) : t("m44", window.I18n.regionName(REGION)));
    paragraph.textContent = description || (feature ? window.I18n.describe(feature, byId) : state.stage === "session"
      ? t("m45")
      : t("m46"));
    if (feature) {
      const city = document.createElement("small");
      city.className = "detail-city";
      city.textContent = featureContext(feature);
      content.replaceChildren(strong, city, paragraph);
    } else content.replaceChildren(strong, paragraph);
  }

  function renderSetup() {
    const descriptions = {
      explore: t("m47", areaWord()),
      cards: t("m48"),
      quiz: t("m49", window.I18n.regionName(REGION))
    };
    if (state.subject === "streets") {
      descriptions.explore = t("m50");
      descriptions.cards = t("m51");
      descriptions.quiz = t("m52");
    }
    for (const button of document.querySelectorAll("[data-mode]")) {
      const active = button.dataset.mode === state.mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    }
    for (const input of $("district-picker").querySelectorAll("input")) input.checked = state.selected.has(input.value);
    for (const input of $("river-picker").querySelectorAll("input")) input.checked = state.selectedRivers.has(input.value);
    $("include-rivers").checked = state.includeRivers;
    $("river-selection").hidden = !state.includeRivers || state.subject === "streets";
    const selectedRiverCount = scopeRivers().filter(river => state.selectedRivers.has(river.id)).length;
    $("river-selection-note").textContent = t("m53", selectedRiverCount, scopeRivers().length);
    const taskCount = selectedFeatures().length;
    const available = scopeFeatures();
    for (const heading of document.querySelectorAll(".district-group-title")) {
      const city = cityById.get(heading.dataset.city);
      heading.textContent = `${cityName(city)} (${scopeFeatures().filter(feature => feature.cityId === city.id).length})`;
    }
    $("city-scope").value = state.scope;
    $("mode-description").textContent = descriptions[state.mode];
    $("select-all").textContent = available.every(feature => state.selected.has(feature.id)) ? t("m40") : t("m41");
    $("selection-note").textContent = state.selected.size === 0 ? state.subject !== "streets" && state.includeRivers && selectedRiverCount ? t("m55", areaWord(true)) : t("m56", areaWord())
      : state.selected.size === available.length ? t("m57", available.length, areaWord(true))
      : t("m58", state.selected.size, available.length, areaWord(true));
    $("selection-note").classList.toggle("error", taskCount === 0);
    $("start-button").disabled = taskCount === 0;
    $("focus-selected").disabled = taskCount === 0;
    $("round-size-field").hidden = state.mode !== "quiz";
    $("round-size").value = String(state.roundSize);
    $("round-size").querySelector('[value="all"]').textContent = state.subject === "streets" ? t("m59") : state.includeRivers ? t("m60", areaWord(true)) : t("m61", areaWord(true));
    $("start-button").firstElementChild.textContent = state.mode === "quiz"
      ? t("m62", roundLength(taskCount))
      : state.mode === "cards" ? t("m63") : t("m64");
    $("street-selection").hidden = state.subject !== "streets";
    $("street-subject-hint").hidden = state.subject !== "streets";
    $("street-subject-hint").textContent = state.streetPath === "levels" ? t("m65") : t("m66");
    for (const button of document.querySelectorAll("[data-subject]")) button.setAttribute("aria-pressed", String(button.dataset.subject === state.subject));
    for (const input of document.querySelectorAll('[name="street-category"]')) input.checked = state.streetCategories.has(input.value);
    for (const input of document.querySelectorAll('[name="street-unit"]')) input.checked = state.streetUnits.has(input.value);
    $("only-bilingual").checked = !german && (state.onlyBilingual || state.language === "en");
    $("only-bilingual").disabled = state.language === "en";
    if (document.activeElement !== $("street-search")) $("street-search").value = state.streetSearch;
    renderStreetPicker();
  }

  function renderSession() {
    const round = state.round;
    const target = byId.get(round.ids[round.position]);
    const parts = nameParts(target);
    const isRiver = target.kind === "river";
    const isStreet = target.kind === "street";
    $("question-city").textContent = (round.level ? t("m67", round.level.number) : "") + featureContext(target);
    $("session-kind").textContent = round.kind === "quiz" ? isStreet ? t("m68") : round.ids.some(id => byId.get(id).kind === "river") ? t("m69") : t("m70") : t("m71");
    $("session-count").textContent = `${round.kind === "quiz" ? t("m73") : t("m74")} ${round.position + 1} / ${round.ids.length}`;
    $("session-score").textContent = round.kind === "quiz" ? t("m75", round.answers.filter(answer => answer.correct).length) : t("m76");
    $("session-progress-bar").style.width = `${100 * (round.position + Number(round.revealed)) / round.ids.length}%`;
    $("question-instruction").textContent = round.kind === "quiz" ? isStreet ? t("m77") : isRiver ? t("m78") : t("m79", areaWord()) : isStreet ? t("m80") : isRiver ? t("m81") : t("m82", areaWord());
    $("question-name").textContent = parts.main;
    $("question-name").lang = parts.lang;
    $("question-name").classList.toggle("english", parts.lang === "en");
    $("question-secondary").textContent = parts.secondary;
    $("question-secondary").hidden = !parts.secondary;
    $("question-hint").hidden = round.revealed;
    $("question-hint").textContent = round.kind === "quiz" ? isStreet ? window.matchMedia("(pointer: coarse)").matches ? t("m83") : t("m84") : isRiver ? t("m85") : t("m86") : t("m87");
    $("reveal-button").textContent = round.kind === "quiz" ? t("m88") : t("m89");
    $("reveal-button").hidden = round.revealed;
    $("next-button").hidden = !round.revealed;
    $("next-button").firstChild.textContent = round.position === round.ids.length - 1 ? t("m90") : t("m91");
    $("feedback").hidden = !round.revealed;
    if (round.revealed) {
      const answer = round.answers.at(-1);
      const heading = document.createElement("strong");
      const description = document.createElement("span");
      heading.textContent = round.kind === "cards" ? readableName(target)
        : answer.correct ? t("m92") : answer.chosenId ? t("m93") : t("m94");
      description.textContent = round.kind === "cards" ? window.I18n.describe(target, byId)
        : answer.correct ? window.I18n.describe(target, byId)
        : t("m95", answer.chosenId ? t("m96", readableName(byId.get(answer.chosenId))) : "", readableName(target), isStreet ? t("m8") : isRiver ? t("m97") : t("m98"));
      $("feedback").replaceChildren(heading, description);
      $("feedback").classList.toggle("wrong", round.kind === "quiz" && !answer.correct);
      renderDetail(target, round.kind === "quiz" ? t("m99", readableName(target)) : null,
        answer.chosenId && !answer.correct ? t("m100", readableName(byId.get(answer.chosenId))) : null);
    } else {
      renderDetail(null, isStreet ? t("m101") : isRiver ? t("m102") : t("m103", areaWord()));
    }
    $("mobile-question-count").textContent = $("session-count").textContent;
    $("mobile-question-city").textContent = $("question-city").textContent;
    $("mobile-question-instruction").textContent = $("question-instruction").textContent;
    $("mobile-question-name").textContent = parts.main;
    $("mobile-question-name").lang = parts.lang;
    $("mobile-question-secondary").textContent = parts.secondary;
    $("mobile-question-feedback").textContent = round.revealed ? $("feedback").firstElementChild.textContent : "";
    $("mobile-question-feedback").classList.toggle("wrong", round.revealed && round.kind === "quiz" && !round.answers.at(-1).correct);
    $("mobile-reveal").hidden = round.revealed;
    $("mobile-reveal").textContent = round.kind === "cards" ? t("m104") : t("m105");
    $("mobile-next").hidden = !round.revealed;
    $("mobile-next").textContent = round.position === round.ids.length - 1 ? t("m90") : t("m91");
  }

  function renderResults() {
    const round = state.round;
    const correct = round.answers.filter(answer => answer.correct).length;
    const errors = round.answers.filter(answer => !answer.correct);
    const scoreText = document.createTextNode(round.kind === "cards" ? String(round.ids.length) : String(correct));
    const total = document.createElement("small");
    total.textContent = round.kind === "cards" ? round.ids.length === 1 ? t("oneCard") : t("m106") : ` / ${round.ids.length}`;
    $("result-score").replaceChildren(scoreText, total);
    $("results-title").textContent = round.kind === "cards" ? t("m108")
      : correct === round.ids.length ? t("m109", window.I18n.regionName(REGION)) : t("m110");
    $("result-summary").textContent = round.kind === "cards" ? t("m111")
      : t("m112", correct, round.ids.length, errors.length ? t("m113", errors.length, errors.length === 1 ? t("m114") : t("m115")) : t("m116"));
    $("result-list").replaceChildren();
    for (const answer of round.answers) {
      const row = document.createElement("div");
      row.className = "result-row" + (round.kind === "quiz" && !answer.correct ? " wrong" : "");
      const name = document.createElement("span");
      name.className = "result-name";
      name.textContent = readableName(byId.get(answer.id));
      const city = document.createElement("small");
      city.textContent = featureContext(byId.get(answer.id));
      name.append(city);
      const status = document.createElement("span");
      status.textContent = round.kind === "cards" ? t("m118") : answer.correct ? t("m119") : t("m120");
      row.append(name, status);
      $("result-list").append(row);
    }
    $("retry-errors").hidden = round.kind !== "quiz" || !errors.length;
    const info = state.subject === "streets" ? streetLevelInfo() : null;
    $("next-street-level").hidden = !round.level || !info || round.level.areaKey !== info.areaKey || round.level.number !== info.level || info.level >= info.total;
    if (round.level) $("result-summary").textContent += t("m121", round.level.areaLabel, round.level.number);
  }

  function render() {
    $("home-view").hidden = state.view !== "home";
    $("practice-view").hidden = state.view !== "practice";
    document.body.dataset.subject = state.subject;
    $("home-street-count").textContent = t("m122", Object.keys(window.STREET_LEVEL_DATA.streets).length.toLocaleString(window.I18n.locale()));
    $("home-data-note").textContent = german && !window.DUESSELDORF_DATA.complete ? t("m123") : german ? t("m124") : t("m125");
    for (const button of document.querySelectorAll("[data-nav]")) {
      if ((state.view === "home" && button.dataset.nav === "home") || (state.view === "practice" && button.dataset.nav === state.mode)) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    }
    $("setup-panel").hidden = state.stage !== "setup";
    $("session-panel").hidden = state.stage !== "session";
    $("results-panel").hidden = state.stage !== "results";
    $("mobile-question").hidden = state.stage !== "session";
    $("language").value = state.language;
    for (const city of cities) $("show-labels-" + city.id).checked = state.labelsByCity[city.id];
    if (german) {
      const input = $("show-neighborhood-labels");
      input.checked = cities.every(city => state.labelsByCity[city.id]);
      input.indeterminate = !input.checked && cities.some(city => state.labelsByCity[city.id]);
    }
    $("show-metro").checked = state.metro;
    for (const input of document.querySelectorAll("[data-transport-kind]")) input.checked = state.metroKinds[input.dataset.transportKind];
    $("show-rivers").checked = riversVisible();
    $("show-rivers").disabled = !rivers.length || currentTarget()?.kind === "river";
    $("show-river-labels").checked = state.riverLabels;
    $("show-river-labels").disabled = !riversVisible();
    $("show-street-labels").checked = state.streetLabels;
    $("show-street-labels").disabled = state.subject === "streets" && state.streetPath === "levels" && state.stage === "session" && state.round.kind === "quiz" && !state.round.revealed;
    $("show-street-labels").title = $("show-street-labels").disabled ? t("m126") : "";
    $("street-credit").hidden = state.subject !== "streets";
    $("river-credit").hidden = !riversVisible();
    $("metro-legend").hidden = !state.metro;
    $("metro-credit").hidden = !state.metro;
    $("metro-legend-items").replaceChildren();
    for (const line of METRO.lines) {
      if (!state.metroKinds[line.kind || "metro"]) continue;
      const chip = document.createElement("span");
      chip.className = "metro-chip";
      chip.dataset.line = line.id;
      const swatch = document.createElement("span");
      swatch.className = "metro-swatch";
      swatch.style.backgroundColor = line.color;
      const code = document.createElement("strong");
      code.textContent = line.code;
      const name = document.createElement("span");
      name.className = "metro-name";
      name.textContent = german ? line.nameZh : state.language === "zh" ? line.nameZh : state.language === "en" ? line.nameEn : `${line.nameZh} · ${line.nameEn}`;
      chip.append(swatch, code, name);
      $("metro-legend-items").append(chip);
    }
    $("city-scope").disabled = state.stage === "session";
    $("city-scope").title = state.stage === "session" ? t("m127") : t("m128");
    $("map-state").textContent = state.stage === "setup" ? t("m129") : state.stage === "results" ? t("m130") : state.round.kind === "quiz" ? t("m131") : t("m132");
    $("map-title").textContent = state.scope === "all" ? window.I18n.regionName(REGION) : german ? byId.get(state.scope).nameZh : cityById.get(state.scope).nameEn;
    $("map-city-zh").textContent = german ? "" : state.scope === "all" ? "臺北市 · 新北市" : cityById.get(state.scope).nameZh;
    $("map-scope-note").textContent = german ? `${scopeFeatures().length} ${scopeFeatures().length === 1 ? t("m21") : t("m20")}` : state.scope === "all" ? t("m134") : t("m135", scopeFeatures().length);
    $("area-level").value = state.areaLevel;
    $("area-level").disabled = state.stage === "session";
    renderSetup();
    if (state.stage === "session") renderSession();
    else if (state.stage === "results") { renderResults(); renderDetail(null, t("m136")); }
    else renderDetail(byId.get(state.inspected));
    $("street-confirmation").hidden = !state.pendingStreet;
    $("street-alternative").hidden = state.streetAlternatives.length < 2;
    map.render();
  }

  function beginRound(kind, ids) {
    const selected = shuffled(ids || selectedFeatures().map(feature => feature.id));
    if (!selected.length) return;
    const level = state.subject === "streets" ? streetLevelInfo() : null;
    state.round = {
      level: level ? { areaKey: level.areaKey, number: level.level, areaLabel: learningAreaLabel() } : null,
      kind,
      ids: kind === "quiz" ? selected.slice(0, roundLength(selected.length)) : selected,
      position: 0, answers: [], revealed: false, completed: false
    };
    state.stage = "session";
    state.inspected = null;
    clearStreetPreview();
    map.reset();
    render();
    $("question-name").setAttribute("tabindex", "-1");
    focusQuestion();
    if (level) $("practice-view").scrollIntoView({ behavior: "instant", block: "start" });
  }

  function focusQuestion() {
    (window.matchMedia("(max-width: 780px)").matches ? $("mobile-question-name") : $("question-name")).focus({ preventScroll: true });
  }

  function selectDistrict(id, options = {}) {
    const feature = byId.get(id);
    if (!feature || !isPlayable(feature)) return;
    if (state.stage === "session" && (feature.kind === "river") !== (currentTarget().kind === "river")) return;
    if (state.stage === "setup") {
      state.inspected = id;
      render();
    } else if (state.stage === "session" && !state.round.revealed) {
      if (feature.kind === "street" && options.touch && state.round.kind === "quiz") {
        state.pendingStreet = id;
        state.streetAlternatives = [...new Set([id, ...(options.alternatives || [])])].filter(candidate => isPlayable(byId.get(candidate)));
        render();
        return;
      }
      answerQuestion(id);
    }
  }

  function answerQuestion(chosenId) {
    const round = state.round;
    if (state.stage !== "session" || round.revealed) return;
    clearStreetPreview();
    const id = round.ids[round.position];
    const answer = { id, chosenId, correct: id === chosenId };
    round.answers.push(answer);
    round.revealed = true;
    if (round.kind === "quiz") {
      const stats = state.progress.districts[id] || { attempts: 0, correct: 0 };
      stats.attempts += 1;
      stats.correct += Number(answer.correct);
      state.progress.districts[id] = stats;
      save(PROGRESS_KEY, state.progress);
    }
    render();
    $("next-button").focus({ preventScroll: true });
  }

  function nextQuestion() {
    const round = state.round;
    if (state.stage !== "session" || !round.revealed) return;
    if (round.position + 1 >= round.ids.length) {
      state.stage = "results";
      if (round.kind === "quiz" && !round.completed) {
        state.progress.rounds += 1;
        save(PROGRESS_KEY, state.progress);
      }
      round.completed = true;
      render();
      if (round.level) $("results-panel").scrollIntoView({ behavior: "instant", block: "start" });
    } else {
      clearStreetPreview();
      round.position += 1;
      round.revealed = false;
      render();
      focusQuestion();
    }
  }

  function endRound() {
    clearStreetPreview();
    state.stage = "setup";
    state.round = null;
    state.inspected = null;
    map.reset();
    render();
  }

  function renderProgress() {
    const rows = Object.values(state.progress.districts);
    const attempts = rows.reduce((sum, row) => sum + row.attempts, 0);
    const correct = rows.reduce((sum, row) => sum + row.correct, 0);
    $("progress-summary").textContent = attempts ? t("m138", attempts, correct, state.progress.rounds)
      : t("m139");
    $("progress-list").replaceChildren();
    let previousCity = null;
    for (const feature of learningFeatures) {
      if (feature.kind === "street" && !state.progress.districts[feature.id]) continue;
      if (feature.kind === "river" && !state.includeRivers && !rivers.some(river => state.progress.districts[river.id])) continue;
      const group = feature.kind === "river" ? "rivers" : feature.kind === "street" ? "streets" : feature.cityId;
      if (group !== previousCity) {
        const heading = document.createElement("h3");
        heading.className = "progress-city";
        heading.textContent = group === "rivers" ? t("m140") : group === "streets" ? t("m141") : cityName(cityById.get(group));
        $("progress-list").append(heading);
        previousCity = group;
      }
      const stats = state.progress.districts[feature.id];
      const row = document.createElement("div");
      row.className = "progress-row";
      const names = document.createElement("div");
      const main = document.createElement("span");
      main.textContent = readableName(feature);
      const summary = document.createElement("small");
      summary.textContent = stats ? t("m142", stats.correct, stats.attempts) : t("m143");
      names.append(main, summary);
      const percentage = document.createElement("span");
      percentage.className = "percentage";
      percentage.textContent = stats ? `${Math.round(stats.correct / stats.attempts * 100)} %` : "—";
      row.append(names, percentage);
      $("progress-list").append(row);
    }
    $("delete-progress").disabled = !attempts;
  }

  function closeMenu() {
    $("main-menu").classList.remove("is-open");
    $("menu-toggle").setAttribute("aria-expanded", "false");
  }

  function navigate(destination) {
    closeMenu();
    if (["progress", "settings", "help"].includes(destination)) {
      if (destination === "progress") { renderProgress(); $("delete-confirmation").hidden = true; }
      if (destination === "settings") $("settings-dialog-content").append($("display-settings"));
      $(destination + "-dialog").showModal();
      return;
    }
    if (destination === "home") state.view = "home";
    else {
      state.view = "practice";
      if (modes.includes(destination) && destination !== state.mode) {
        state.stage = "setup";
        state.round = null;
        clearStreetPreview();
        state.mode = destination;
      }
    }
    saveSettings();
    render();
    if (state.view === "practice") map.reset();
    window.scrollTo({ top: 0, behavior: "instant" });
  }

  async function withLoading(action) {
    const loading = $("chapter-loading");
    if (!loading.hidden) return;
    loading.hidden = false;
    document.body.setAttribute("aria-busy", "true");
    // Yield across a paint before the expensive initial geometry preparation.
    await new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 40)));
    try { action(); }
    finally { loading.hidden = true; document.body.removeAttribute("aria-busy"); }
  }

  function chooseSubject(subject) {
    state.subject = subject;
    state.stage = "setup";
    state.round = null;
    state.inspected = null;
    clearStreetPreview();
    saveSettings();
    render();
    map.reset();
  }

  $("street-learning-path").addEventListener("change", event => {
    state.streetPath = event.target.value; state.streetLimit = 40; state.inspected = null;
    clearStreetPreview(); saveSettings(); render(); map.reset();
  });
  $("street-level").addEventListener("change", event => setStreetLevel(Number(event.target.value)));
  $("level-previous").addEventListener("click", () => setStreetLevel(streetLevelInfo().level - 1));
  $("level-next").addEventListener("click", () => setStreetLevel(streetLevelInfo().level + 1));
  $("level-review").addEventListener("change", event => { state.levelReview = event.target.checked; clearStreetPreview(); saveSettings(); render(); });
  $("next-street-level").addEventListener("click", () => {
    const kind = state.round.kind; const next = streetLevelInfo().level + 1;
    endRound(); setStreetLevel(next); beginRound(kind);
  });
  $("area-level").addEventListener("change", event => {
    state.areaLevel = event.target.value;
    state.selected = new Set(scopeFeatures().map(feature => feature.id));
    state.inspected = null;
    clearStreetPreview();
    buildPicker(); saveSettings(); map.reset(); render();
  });
  buildPicker();
  for (const button of document.querySelectorAll("[data-nav]")) button.addEventListener("click", () => ["explore", "cards", "quiz"].includes(button.dataset.nav) ? withLoading(() => navigate(button.dataset.nav)) : navigate(button.dataset.nav));
  for (const button of document.querySelectorAll("[data-subject]")) button.addEventListener("click", () => withLoading(() => chooseSubject(button.dataset.subject)));
  for (const button of document.querySelectorAll("[data-start]")) button.addEventListener("click", () => withLoading(() => {
    const subject = button.dataset.start;
    state.view = "practice";
    state.mode = "explore";
    if (subject === "rivers") { state.includeRivers = true; state.rivers = true; state.selected.clear(); }
    else if (subject === "districts") {
      state.includeRivers = false;
      if (!state.selected.size) state.selected = new Set(scopeFeatures().map(feature => feature.id));
    } else if (!state.selected.size) state.selected = new Set(scopeFeatures().map(feature => feature.id));
    chooseSubject(subject === "streets" ? "streets" : "districts");
    window.scrollTo({ top: 0, behavior: "instant" });
  }));
  document.querySelector(".brand").addEventListener("click", event => { event.preventDefault(); navigate("home"); });
  $("menu-toggle").addEventListener("click", () => {
    const open = $("main-menu").classList.toggle("is-open");
    $("menu-toggle").setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("keydown", event => { if (event.key === "Escape") closeMenu(); });
  $("settings-dialog").addEventListener("close", () => $("inline-settings-slot").append($("display-settings")));
  $("help-sources").addEventListener("click", () => { $("help-dialog").close(); $("sources-dialog").showModal(); });
  for (const [name, key] of [["street-category", "streetCategories"], ["street-unit", "streetUnits"]]) {
    for (const input of document.querySelectorAll(`[name="${name}"]`)) input.addEventListener("change", () => {
      input.checked ? state[key].add(input.value) : state[key].delete(input.value);
      state.streetLimit = 40;
      clearStreetPreview();
      saveSettings();
      render();
    });
  }
  $("only-bilingual").addEventListener("change", event => { state.onlyBilingual = event.target.checked; saveSettings(); render(); });
  let streetSearchTimer;
  $("street-search").addEventListener("input", event => {
    state.streetSearch = event.target.value.slice(0, 120);
    state.streetLimit = 40;
    clearTimeout(streetSearchTimer);
    streetSearchTimer = setTimeout(() => { saveSettings(); render(); }, 120);
  });
  $("street-select-all").addEventListener("click", () => {
    const candidates = streetCandidates().features;
    const allSelected = candidates.every(feature => !state.excludedStreets.has(feature.id));
    for (const feature of candidates) allSelected ? state.excludedStreets.add(feature.id) : state.excludedStreets.delete(feature.id);
    streetRevision++;
    saveSettings();
    render();
  });
  $("street-more").addEventListener("click", () => { state.streetLimit += 60; renderStreetPicker(); });
  $("show-street-labels").addEventListener("change", event => { state.streetLabels = event.target.checked; saveSettings(); render(); });
  $("street-confirm").addEventListener("click", () => { if (state.pendingStreet) answerQuestion(state.pendingStreet); });
  $("street-alternative").addEventListener("click", () => {
    const index = state.streetAlternatives.indexOf(state.pendingStreet);
    state.pendingStreet = state.streetAlternatives[(index + 1) % state.streetAlternatives.length];
    render();
  });
  $("export-progress").addEventListener("click", () => {
    const payload = { app: "taipei-kennen", region: REGION.id, formatVersion: 1, exportedAt: new Date().toISOString(), progress: state.progress, streetLearning: { version: 1, levels: state.streetLevels } };
    const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${REGION.storagePrefix}-lernstand-${new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Berlin" }).format(new Date())}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  let importedProgress = null;
  let importedStreetLearning = null;
  $("import-progress").addEventListener("change", async event => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 5 * 1024 * 1024) throw new Error(t("m148"));
      let payload;
      try { payload = JSON.parse(await file.text()); }
      catch { throw new Error(t("m149")); }
      if (payload?.app !== "taipei-kennen" || payload.formatVersion !== 1 || !payload.progress || !payload.progress.districts || typeof payload.progress.districts !== "object" || Array.isArray(payload.progress.districts)) throw new Error(t("m149"));
      if ((payload.region || "taipei") !== REGION.id) throw new Error(t("m150"));
      if (payload.streetLearning && payload.streetLearning.version !== 1) throw new Error(t("m151"));
      importedStreetLearning = payload.streetLearning ? cleanStreetLevels(payload.streetLearning.levels) : null;
      importedProgress = cleanProgress(payload.progress);
      const attempts = Object.values(importedProgress.districts).reduce((total, row) => total + row.attempts, 0);
      $("import-summary").textContent = t("m152", attempts, importedProgress.rounds);
      $("import-confirmation").hidden = false;
      $("confirm-import").focus();
    } catch (error) { toast(error.message || t("m153")); }
    event.target.value = "";
  });
  $("confirm-import").addEventListener("click", () => {
    if (!importedProgress || !save(PROGRESS_KEY, importedProgress)) return;
    state.progress = importedProgress;
    if (importedStreetLearning) { state.streetLevels = importedStreetLearning; saveSettings(); }
    importedStreetLearning = null;
    importedProgress = null;
    $("import-confirmation").hidden = true;
    if (state.stage !== "setup") endRound();
    else render();
    renderProgress();
    toast(t("m154"));
  });
  $("cancel-import").addEventListener("click", () => { importedProgress = null; $("import-confirmation").hidden = true; });
  for (const button of document.querySelectorAll("[data-mode]")) button.addEventListener("click", () => {
    state.mode = button.dataset.mode;
    saveSettings();
    render();
  });
  $("select-all").addEventListener("click", () => {
    const available = scopeFeatures();
    state.selected = new Set(available.every(feature => state.selected.has(feature.id)) ? [] : available.map(feature => feature.id));
    if (state.inspected && !state.selected.has(state.inspected)) state.inspected = null;
    saveSettings();
    render();
  });
  $("city-scope").addEventListener("change", event => {
    state.scope = event.target.value;
    state.selected = new Set(scopeFeatures().map(feature => feature.id));
    state.inspected = null;
    buildPicker();
    saveSettings();
    map.reset();
    render();
  });
  $("focus-selected").addEventListener("click", () => map.fit(state.subject === "streets"
    ? [...state.selected].map(id => byId.get(id)) : selectedFeatures()));
  $("include-rivers").addEventListener("change", event => {
    state.includeRivers = event.target.checked;
    if (state.includeRivers) state.rivers = true;
    if (state.inspected && !isPlayable(byId.get(state.inspected))) state.inspected = null;
    saveSettings();
    render();
  });
  $("language").addEventListener("change", event => {
    state.language = event.target.value;
    saveSettings();
    render();
  });
  if (german) $("show-neighborhood-labels").addEventListener("change", event => {
    for (const city of cities) state.labelsByCity[city.id] = event.target.checked;
    saveSettings(); render();
  });
  for (const city of cities) $("show-labels-" + city.id).addEventListener("change", event => {
    state.labelsByCity[city.id] = event.target.checked;
    saveSettings();
    render();
  });
  for (const input of document.querySelectorAll("[data-transport-kind]")) input.addEventListener("change", event => { state.metroKinds[input.dataset.transportKind] = event.target.checked; saveSettings(); render(); });
  $("show-metro").addEventListener("change", event => {
    state.metro = event.target.checked;
    saveSettings();
    render();
  });
  $("show-rivers").addEventListener("change", event => {
    state.rivers = event.target.checked;
    saveSettings();
    render();
  });
  $("show-river-labels").addEventListener("change", event => {
    state.riverLabels = event.target.checked;
    saveSettings();
    render();
  });
  $("round-size").addEventListener("change", event => { state.roundSize = event.target.value === "all" ? "all" : Number(event.target.value); saveSettings(); renderSetup(); });
  $("start-button").addEventListener("click", () => {
    if (state.mode === "explore") { state.inspected = null; map.reset(); render(); }
    else beginRound(state.mode);
  });
  $("reveal-button").addEventListener("click", () => answerQuestion(null));
  $("mobile-reveal").addEventListener("click", () => answerQuestion(null));
  $("mobile-next").addEventListener("click", nextQuestion);
  $("next-button").addEventListener("click", nextQuestion);
  $("session-end").addEventListener("click", endRound);
  $("back-to-setup").addEventListener("click", endRound);
  $("retry-errors").addEventListener("click", () => beginRound("quiz", state.round.answers.filter(answer => !answer.correct).map(answer => answer.id)));
  for (const [button, dialog] of [["progress-open", "progress-dialog"], ["sources-open", "sources-dialog"]]) {
    $(button).addEventListener("click", () => {
      if (dialog === "progress-dialog") { renderProgress(); $("delete-confirmation").hidden = true; }
      $(dialog).showModal();
    });
  }
  for (const button of document.querySelectorAll(".dialog-close")) button.addEventListener("click", () => button.closest("dialog").close());
  $("delete-progress").addEventListener("click", () => { $("delete-confirmation").hidden = false; $("delete-confirm").focus(); });
  $("delete-cancel").addEventListener("click", () => { $("delete-confirmation").hidden = true; $("delete-progress").focus(); });
  $("delete-confirm").addEventListener("click", () => {
    try { localStorage.removeItem(PROGRESS_KEY); }
    catch { toast(t("m155")); return; }
    state.progress = cleanProgress(null);
    state.streetLevels = {}; saveSettings();
    $("delete-confirmation").hidden = true;
    if (state.stage !== "setup") endRound();
    else render();
    renderProgress();
    toast(t("m156"));
  });
  map.reset();
  render();
})();
