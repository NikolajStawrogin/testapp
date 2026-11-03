(() => {
  "use strict";

  const DATA = window.TAIPEI_DATA;
  const METRO = window.TAIPEI_METRO;
  const features = DATA.features;
  const rivers = window.TAIPEI_RIVERS.features;
  const learningFeatures = [...features, ...rivers];
  const cities = DATA.cities;
  const byId = new Map(learningFeatures.map(feature => [feature.id, feature]));
  const cityById = new Map(cities.map(city => [city.id, city]));
  const $ = id => document.getElementById(id);
  const SVG_NS = "http://www.w3.org/2000/svg";
  const PROGRESS_KEY = "taipei-kennen.progress.v1";
  const SETTINGS_KEY = "taipei-kennen.settings.v1";
  const MIN_MAP_ZOOM = 0.5;
  const MAX_MAP_ZOOM = 12;
  const modes = ["explore", "cards", "quiz"];
  const languages = ["both", "zh", "en"];
  let toastTimer;

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
      toast("Der Browser kann deinen Fortschritt gerade nicht speichern. Die Übung funktioniert trotzdem.");
      return false;
    }
  }

  function count(value) {
    return Number.isSafeInteger(value) && value >= 0 ? value : 0;
  }

  function cleanProgress(raw) {
    const result = { rounds: count(raw?.rounds), districts: {} };
    for (const feature of learningFeatures) {
      const row = raw?.districts?.[feature.id];
      if (!row || !count(row.attempts)) continue;
      result.districts[feature.id] = {
        attempts: count(row.attempts),
        correct: Math.min(count(row.correct), count(row.attempts))
      };
    }
    return result;
  }

  const savedSettings = load(SETTINGS_KEY);
  const legacyTaipei = features.filter(feature => feature.cityId === "taipei");
  const storedIds = Array.isArray(savedSettings?.selected) ? savedSettings.selected.filter(id => byId.has(id) && byId.get(id).kind !== "river") : null;
  const expandLegacyAll = savedSettings?.datasetVersion !== DATA.version && storedIds?.length === legacyTaipei.length
    && legacyTaipei.every(feature => storedIds.includes(feature.id));
  const initialIds = !storedIds || expandLegacyAll ? features.map(feature => feature.id) : storedIds;
  const storedScope = ["all", ...cities.map(city => city.id)].includes(savedSettings?.scope) ? savedSettings.scope : null;
  const initialScope = expandLegacyAll ? "all" : storedScope || (initialIds.length && initialIds.every(id => byId.get(id).cityId === "taipei") ? "taipei" : "all");
  const state = {
    stage: "setup",
    mode: modes.includes(savedSettings?.mode) ? savedSettings.mode : "explore",
    language: languages.includes(savedSettings?.language) ? savedSettings.language : "both",
    labelsByCity: Object.fromEntries(cities.map(city => [city.id,
      typeof savedSettings?.labelsByCity?.[city.id] === "boolean"
        ? savedSettings.labelsByCity[city.id] : savedSettings?.labels !== false])),
    metro: savedSettings?.metro !== false,
    rivers: savedSettings?.rivers !== false,
    riverLabels: savedSettings?.riverLabels !== false,
    includeRivers: savedSettings?.includeRivers === true,
    selectedRivers: new Set(Array.isArray(savedSettings?.selectedRivers)
      ? savedSettings.selectedRivers.filter(id => rivers.some(river => river.id === id)) : rivers.map(river => river.id)),
    scope: initialScope,
    selected: new Set(initialIds.filter(id => initialScope === "all" || byId.get(id).cityId === initialScope)),
    roundSize: savedSettings?.roundSize === "all" || savedSettings?.roundSize === 12 ? "all"
      : [5, 10].includes(savedSettings?.roundSize) ? savedSettings.roundSize : 10,
    inspected: null,
    round: null,
    progress: cleanProgress(load(PROGRESS_KEY))
  };

  function saveSettings() {
    save(SETTINGS_KEY, {
      mode: state.mode, language: state.language, labelsByCity: state.labelsByCity, metro: state.metro,
      rivers: state.rivers, riverLabels: state.riverLabels, includeRivers: state.includeRivers,
      selectedRivers: [...state.selectedRivers],
      selected: [...state.selected], roundSize: state.roundSize,
      scope: state.scope, datasetVersion: DATA.version
    });
  }

  function scopeFeatures() {
    return state.scope === "all" ? features : features.filter(feature => feature.cityId === state.scope);
  }

  function scopeRivers() {
    return rivers.filter(river => state.scope === "all" || river.cityIds.includes(state.scope));
  }

  function selectedFeatures() {
    return [...state.selected].map(id => byId.get(id)).concat(state.includeRivers
      ? scopeRivers().filter(river => state.selectedRivers.has(river.id)) : []);
  }

  function isPlayable(feature) {
    return feature.kind === "river" ? state.includeRivers && state.selectedRivers.has(feature.id)
      && (state.scope === "all" || feature.cityIds.includes(state.scope)) : state.selected.has(feature.id);
  }

  function currentTarget() {
    return state.stage === "session" ? byId.get(state.round.ids[state.round.position]) : null;
  }

  function riversVisible() {
    return state.rivers || currentTarget()?.kind === "river";
  }

  function featureContext(feature) {
    return feature.kind === "river" ? "Fluss · " + feature.cityIds.map(id => cityName(cityById.get(id))).join(" / ")
      : cityName(cityById.get(feature.cityId));
  }

  function roundLength(size) {
    return state.roundSize === "all" ? size : Math.min(state.roundSize, size);
  }

  function cityName(city) {
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
    if (state.language === "en") return { main: feature.nameEn, secondary: "", lang: "en" };
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
        path.setAttribute("fill", feature.cityId === "taipei" ? colors[index % colors.length] : newTaipeiColors[index % newTaipeiColors.length]);
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
        zh.setAttribute("lang", "zh-Hant");
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
        if (!pointer || pointer.id !== event.pointerId) return;
        if (!pointer.dragged && Math.hypot(event.clientX - pointer.clientX, event.clientY - pointer.clientY) < 5) return;
        if (!pointer.dragged) {
          pointer.dragged = true;
          this.svg.setPointerCapture(event.pointerId);
          this.svg.classList.add("dragging");
        }
        const point = this.svgPoint(event.clientX, event.clientY);
        this.x = pointer.x + point.x - pointer.point.x;
        this.y = pointer.y + point.y - pointer.point.y;
        this.applyTransform();
      });
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
        $("map-instruction").textContent = "Zwei Finger: Zoom · Ein Finger: Verschieben";
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
          $("metro-casings").append(casing);
          const path = document.createElementNS(SVG_NS, "path");
          path.setAttribute("d", d);
          path.setAttribute("class", "metro-line");
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
        zh.setAttribute("lang", "zh-Hant");
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
        this.zoom = Math.max(MIN_MAP_ZOOM, Math.min(MAX_MAP_ZOOM, this.pinch.zoom * distance / this.pinch.distance));
        this.x = center.x - this.pinch.point.x * this.zoom;
        this.y = center.y - this.pinch.point.y * this.zoom;
        this.svg.classList.add("dragging");
        this.applyTransform();
      } else if (this.pointer?.id === event.pointerId) {
        const pointer = this.pointer;
        if (!pointer.dragged && Math.hypot(event.clientX - pointer.clientX, event.clientY - pointer.clientY) < 5) return;
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
      if (tapId) this.onSelect(tapId);
    }

    svgPoint(clientX, clientY) {
      const point = this.svg.createSVGPoint();
      point.x = clientX;
      point.y = clientY;
      return point.matrixTransform(this.svg.getScreenCTM().inverse());
    }

    selectionAt(event) {
      if (riversVisible() && ((state.stage === "setup" && state.includeRivers) || currentTarget()?.kind === "river")) {
        const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(this.content.getScreenCTM().inverse());
        const containing = rivers.filter(river => this.paths.get(river.id).isPointInFill(point));
        // A wider touch target must never cover another river's actual water surface.
        if (containing.length) return containing.find(isPlayable)?.id || null;
      }
      return event.target.closest(".district-shape, .river-hit")?.dataset.id;
    }

    zoomBy(factor, point = { x: 500, y: 390 }) {
      const newZoom = Math.max(MIN_MAP_ZOOM, Math.min(MAX_MAP_ZOOM, this.zoom * factor));
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
      $("zoom-in").disabled = this.zoom >= MAX_MAP_ZOOM;
      $("zoom-out").disabled = this.zoom <= MIN_MAP_ZOOM;
      $("zoom-range").value = String(Math.round(this.zoom * 100));
      $("zoom-level").textContent = `${Math.round(this.zoom * 100)} %`;
      this.updateLabels();
    }

    reset() {
      this.fit(scopeFeatures());
    }

    fit(selected) {
      if (!selected.length) return;
      const [minX, minY, maxX, maxY] = extent(selected.flatMap(feature => {
        const box = this.extents.get(feature.id);
        return [[box[0], box[1]], [box[2], box[3]]];
      }));
      const desired = Math.min(870 / (maxX - minX), 680 / (maxY - minY));
      this.zoom = Math.max(MIN_MAP_ZOOM, Math.min(MAX_MAP_ZOOM, Math.abs(desired - 1) < 1e-8 ? 1 : desired));
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
      for (const feature of learningFeatures) {
        const label = this.labels.get(feature.id);
        label.group.style.display = "none";
        const enabled = feature.kind === "river" ? riversVisible() && state.riverLabels : state.labelsByCity[feature.cityId];
        if (!enabled || (inSession && !revealed && feature.id === target)) continue;
        label.zh.style.display = state.language === "en" ? "none" : "";
        label.en.style.display = state.language === "zh" ? "none" : "";
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
      $("river-layer").style.display = riversVisible() ? "" : "none";
      const inSession = state.stage === "session";
      const target = inSession ? state.round.ids[state.round.position] : null;
      const revealed = inSession && state.round.revealed;
      const answer = revealed ? state.round.answers.at(-1) : null;
      for (const feature of learningFeatures) {
        const isRiver = feature.kind === "river";
        const active = isPlayable(feature) && (!inSession || isRiver === (byId.get(target).kind === "river"));
        const path = this.paths.get(feature.id);
        path.classList.toggle("is-muted", !active && !isRiver);
        path.classList.toggle("is-selected", !inSession && feature.id === state.inspected);
        path.classList.toggle("is-correct", revealed && target === feature.id);
        path.classList.toggle("is-wrong", revealed && !answer.correct && answer.chosenId === feature.id);
        const control = isRiver ? this.labels.get(feature.id).hit : path;
        if (isRiver) control.style.pointerEvents = active && !revealed && riversVisible() ? "all" : "none";
        control.setAttribute("tabindex", active && !revealed && (!isRiver || riversVisible()) ? "0" : "-1");
        control.setAttribute("aria-disabled", String(!active || revealed));
        control.setAttribute("aria-label", inSession && !revealed ? isRiver ? "Fluss auf der Karte auswählen" : "Bezirk auf der Karte auswählen" : readableName(feature));
      }
      this.updateLabels();
    }
  }

  const map = new DistrictMap(selectDistrict);

  function buildPicker() {
    const root = $("district-picker");
    root.replaceChildren();
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
      zh.lang = "zh-Hant";
      zh.textContent = feature.nameZh;
      const en = document.createElement("small");
      en.lang = "en";
      en.textContent = feature.nameEn.replace(" Dist.", "");
      label.append(input, zh, en);
      return label;
  }

  function renderDetail(feature, title) {
    const content = $("map-detail").lastElementChild;
    const strong = document.createElement("strong");
    const paragraph = document.createElement("p");
    strong.textContent = title || (feature ? readableName(feature) : "Ein Gefühl für Taipei bekommen");
    paragraph.textContent = feature ? feature.description : state.stage === "session"
      ? "Die gesuchte Fläche wird nach deiner Antwort aufgelöst."
      : "Klicke auf einen Bezirk oder einen zum Mitüben gewählten Fluss, um Namen und Lage kennenzulernen.";
    if (feature) {
      const city = document.createElement("small");
      city.className = "detail-city";
      city.textContent = featureContext(feature);
      content.replaceChildren(strong, city, paragraph);
    } else content.replaceChildren(strong, paragraph);
  }

  function renderSetup() {
    const descriptions = {
      explore: "Erkunde die Karte und klicke auf einen Bezirk.",
      cards: "Präge dir Namen und Lage ein. Lass dir die richtige Fläche zeigen.",
      quiz: "Ein Name, eine Fläche. Teste, wie gut du Taipei schon kennst."
    };
    for (const button of document.querySelectorAll("[data-mode]")) {
      const active = button.dataset.mode === state.mode;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    }
    for (const input of $("district-picker").querySelectorAll("input")) input.checked = state.selected.has(input.value);
    for (const input of $("river-picker").querySelectorAll("input")) input.checked = state.selectedRivers.has(input.value);
    $("include-rivers").checked = state.includeRivers;
    $("river-selection").hidden = !state.includeRivers;
    const selectedRiverCount = scopeRivers().filter(river => state.selectedRivers.has(river.id)).length;
    $("river-selection-note").textContent = `${selectedRiverCount} von ${scopeRivers().length} Flüssen ausgewählt. Für eine reine Flussrunde die Bezirksauswahl aufheben.`;
    const taskCount = selectedFeatures().length;
    const available = scopeFeatures();
    for (const heading of document.querySelectorAll(".district-group-title")) {
      const city = cityById.get(heading.dataset.city);
      heading.textContent = `${cityName(city)} (${features.filter(feature => feature.cityId === city.id).length})`;
    }
    $("city-scope").value = state.scope;
    $("mode-description").textContent = descriptions[state.mode];
    $("select-all").textContent = available.every(feature => state.selected.has(feature.id)) ? "Auswahl aufheben" : "Alle auswählen";
    $("selection-note").textContent = state.selected.size === 0 ? state.includeRivers && selectedRiverCount ? "Keine Bezirke · nur Flüsse üben" : "Wähle mindestens einen Bezirk oder Fluss."
      : state.selected.size === available.length ? `Alle ${available.length} Bezirke ausgewählt`
      : `${state.selected.size} von ${available.length} Bezirken ausgewählt`;
    $("selection-note").classList.toggle("error", taskCount === 0);
    $("start-button").disabled = taskCount === 0;
    $("focus-selected").disabled = taskCount === 0;
    $("round-size-field").hidden = state.mode !== "quiz";
    $("round-size").value = String(state.roundSize);
    $("round-size").querySelector('[value="all"]').textContent = state.includeRivers ? "Alle gewählten Bezirke und Flüsse" : "Alle gewählten Bezirke";
    $("start-button").firstElementChild.textContent = state.mode === "quiz"
      ? `Quiz starten · ${roundLength(taskCount)} Aufgaben`
      : state.mode === "cards" ? "Lernkarten starten" : "Karte erkunden";
  }

  function renderSession() {
    const round = state.round;
    const target = byId.get(round.ids[round.position]);
    const parts = nameParts(target);
    const isRiver = target.kind === "river";
    $("question-city").textContent = featureContext(target);
    $("session-kind").textContent = round.kind === "quiz" ? round.ids.some(id => byId.get(id).kind === "river") ? "DEIN KARTENQUIZ" : "DEIN BEZIRKSQUIZ" : "DEINE LERNKARTEN";
    $("session-count").textContent = `${round.kind === "quiz" ? "Aufgabe" : "Karte"} ${round.position + 1} / ${round.ids.length}`;
    $("session-score").textContent = round.kind === "quiz" ? `${round.answers.filter(answer => answer.correct).length} richtig` : "Ohne Bewertung";
    $("session-progress-bar").style.width = `${100 * (round.position + Number(round.revealed)) / round.ids.length}%`;
    $("question-instruction").textContent = round.kind === "quiz" ? isRiver ? "Finde diesen Fluss auf der Karte:" : "Finde diesen Bezirk auf der Karte:" : isRiver ? "Wo verläuft dieser Fluss?" : "Wo liegt dieser Bezirk?";
    $("question-name").textContent = parts.main;
    $("question-name").lang = parts.lang;
    $("question-name").classList.toggle("english", parts.lang === "en");
    $("question-secondary").textContent = parts.secondary;
    $("question-secondary").hidden = !parts.secondary;
    $("question-hint").hidden = round.revealed;
    $("question-hint").textContent = round.kind === "quiz" ? isRiver ? "Klicke auf den passenden blauen Flusslauf. Du kannst vorher zoomen." : "Klicke auf die passende Fläche. Du kannst vorher zoomen." : "Versuche ihn zu finden oder lass dir seine Lage zeigen.";
    $("reveal-button").textContent = round.kind === "quiz" ? "Ich weiß es noch nicht" : "Lage auf der Karte zeigen";
    $("reveal-button").hidden = round.revealed;
    $("next-button").hidden = !round.revealed;
    $("next-button").firstChild.textContent = round.position === round.ids.length - 1 ? "Runde abschließen" : "Weiter";
    $("feedback").hidden = !round.revealed;
    if (round.revealed) {
      const answer = round.answers.at(-1);
      const heading = document.createElement("strong");
      const description = document.createElement("span");
      heading.textContent = round.kind === "cards" ? readableName(target)
        : answer.correct ? "Genau richtig!" : answer.chosenId ? "Noch nicht ganz." : "Für die nächste Runde merken.";
      description.textContent = round.kind === "cards" ? target.description
        : answer.correct ? target.description
        : `${answer.chosenId ? `Gewählt: ${readableName(byId.get(answer.chosenId))}. ` : ""}Gesucht: ${readableName(target)}. Die richtige Fläche ist grün markiert.`;
      $("feedback").replaceChildren(heading, description);
      $("feedback").classList.toggle("wrong", round.kind === "quiz" && !answer.correct);
      renderDetail(target);
    } else {
      renderDetail(null, isRiver ? "Welcher Fluss ist gesucht?" : "Welcher Bezirk ist gesucht?");
    }
  }

  function renderResults() {
    const round = state.round;
    const correct = round.answers.filter(answer => answer.correct).length;
    const errors = round.answers.filter(answer => !answer.correct);
    const scoreText = document.createTextNode(round.kind === "cards" ? String(round.ids.length) : String(correct));
    const total = document.createElement("small");
    total.textContent = round.kind === "cards" ? " Karten" : ` / ${round.ids.length}`;
    $("result-score").replaceChildren(scoreText, total);
    $("results-title").textContent = round.kind === "cards" ? "Ein Stück vertrauter."
      : correct === round.ids.length ? "Taipei wird vertrauter!" : "Jede Runde bringt dich weiter.";
    $("result-summary").textContent = round.kind === "cards" ? "Du hast dir alle gewählten Orte angesehen. Im Quiz kannst du dein Wissen testen."
      : `${correct} von ${round.ids.length} richtig.${errors.length ? ` ${errors.length} ${errors.length === 1 ? "Aufgabe wartet" : "Aufgaben warten"} noch auf eine Wiederholung.` : " Alle Orte dieser Runde gefunden."}`;
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
      status.textContent = round.kind === "cards" ? "Angesehen" : answer.correct ? "Richtig" : "Wiederholen";
      row.append(name, status);
      $("result-list").append(row);
    }
    $("retry-errors").hidden = round.kind !== "quiz" || !errors.length;
  }

  function render() {
    $("setup-panel").hidden = state.stage !== "setup";
    $("session-panel").hidden = state.stage !== "session";
    $("results-panel").hidden = state.stage !== "results";
    $("language").value = state.language;
    for (const city of cities) $("show-labels-" + city.id).checked = state.labelsByCity[city.id];
    $("show-metro").checked = state.metro;
    $("show-rivers").checked = riversVisible();
    $("show-rivers").disabled = currentTarget()?.kind === "river";
    $("show-river-labels").checked = state.riverLabels;
    $("show-river-labels").disabled = !riversVisible();
    $("river-credit").hidden = !riversVisible();
    $("metro-legend").hidden = !state.metro;
    $("metro-credit").hidden = !state.metro;
    $("metro-legend-items").replaceChildren();
    for (const line of METRO.lines) {
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
      name.textContent = state.language === "zh" ? line.nameZh : state.language === "en" ? line.nameEn : `${line.nameZh} · ${line.nameEn}`;
      chip.append(swatch, code, name);
      $("metro-legend-items").append(chip);
    }
    $("map-state").textContent = state.stage === "setup" ? "Entdecken" : state.stage === "results" ? "Rundenauswertung" : state.round.kind === "quiz" ? "Quiz" : "Lernkarten";
    $("map-title").textContent = state.scope === "all" ? "Taipei & New Taipei" : cityById.get(state.scope).nameEn;
    $("map-city-zh").textContent = state.scope === "all" ? "臺北市 · 新北市" : cityById.get(state.scope).nameZh;
    $("map-scope-note").textContent = state.scope === "all" ? "12 + 29 Bezirke · beide Städte" : `${scopeFeatures().length} Bezirke`;
    renderSetup();
    if (state.stage === "session") renderSession();
    else if (state.stage === "results") { renderResults(); renderDetail(null, "Deine nächste Runde wartet."); }
    else renderDetail(byId.get(state.inspected));
    map.render();
  }

  function beginRound(kind, ids) {
    const selected = shuffled(ids || selectedFeatures().map(feature => feature.id));
    if (!selected.length) return;
    state.round = {
      kind,
      ids: kind === "quiz" ? selected.slice(0, roundLength(selected.length)) : selected,
      position: 0, answers: [], revealed: false, completed: false
    };
    state.stage = "session";
    state.inspected = null;
    map.reset();
    render();
    $("question-name").setAttribute("tabindex", "-1");
    $("question-name").focus({ preventScroll: true });
  }

  function selectDistrict(id) {
    const feature = byId.get(id);
    if (!feature || !isPlayable(feature)) return;
    if (state.stage === "session" && (feature.kind === "river") !== (currentTarget().kind === "river")) return;
    if (state.stage === "setup") {
      state.inspected = id;
      render();
    } else if (state.stage === "session" && !state.round.revealed) {
      answerQuestion(id);
    }
  }

  function answerQuestion(chosenId) {
    const round = state.round;
    if (state.stage !== "session" || round.revealed) return;
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
    } else {
      round.position += 1;
      round.revealed = false;
      render();
      $("question-name").focus({ preventScroll: true });
    }
  }

  function endRound() {
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
    $("progress-summary").textContent = attempts ? `${attempts} beantwortete Aufgaben · ${correct} richtig · ${state.progress.rounds} abgeschlossene Quizrunden`
      : "Deine ersten Quizantworten werden hier gespeichert. Lernkarten werden nicht bewertet.";
    $("progress-list").replaceChildren();
    let previousCity = null;
    for (const feature of learningFeatures) {
      if (feature.kind === "river" && !state.includeRivers && !rivers.some(river => state.progress.districts[river.id])) continue;
      const group = feature.kind === "river" ? "rivers" : feature.cityId;
      if (group !== previousCity) {
        const heading = document.createElement("h3");
        heading.className = "progress-city";
        heading.textContent = group === "rivers" ? "Flüsse" : cityName(cityById.get(group));
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
      summary.textContent = stats ? `${stats.correct} von ${stats.attempts} Antworten richtig` : "Noch nicht geübt";
      names.append(main, summary);
      const percentage = document.createElement("span");
      percentage.className = "percentage";
      percentage.textContent = stats ? `${Math.round(stats.correct / stats.attempts * 100)} %` : "—";
      row.append(names, percentage);
      $("progress-list").append(row);
    }
    $("delete-progress").disabled = !attempts;
  }

  buildPicker();
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
  $("focus-selected").addEventListener("click", () => map.fit(selectedFeatures()));
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
  for (const city of cities) $("show-labels-" + city.id).addEventListener("change", event => {
    state.labelsByCity[city.id] = event.target.checked;
    saveSettings();
    render();
  });
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
    catch { toast("Der Browserspeicher konnte nicht gelöscht werden."); return; }
    state.progress = cleanProgress(null);
    $("delete-confirmation").hidden = true;
    renderProgress();
    toast("Dein Lernfortschritt wurde gelöscht.");
  });
  map.reset();
  render();
})();
