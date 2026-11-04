/* Local vector streets: viewport rendering, full-unit hover and geographic picking. */
(() => {
  "use strict";
  const t = window.I18n.t;
  const NS = "http://www.w3.org/2000/svg";
  const node = (tag, attributes = {}) => {
    const element = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
    return element;
  };
  const overlaps = (a, b) => a[0] <= b[2] && a[2] >= b[0] && a[1] <= b[3] && a[3] >= b[1];
  const bounds = points => points.reduce((box, point) => [Math.min(box[0], point[0]), Math.min(box[1], point[1]), Math.max(box[2], point[0]), Math.max(box[3], point[1])], [Infinity, Infinity, -Infinity, -Infinity]);

  // Fixed world-space cells avoid scanning the entire city after each gesture.
  class SpatialIndex {
    constructor(items) {
      this.cells = new Map();
      for (const item of items) {
        const [left, top, right, bottom] = item.bounds.map(value => Math.floor(value / 64));
        for (let x = left; x <= right; x++) for (let y = top; y <= bottom; y++) {
          const key = `${x},${y}`;
          if (!this.cells.has(key)) this.cells.set(key, []);
          this.cells.get(key).push(item);
        }
      }
    }
    query(view) {
      const found = new Set();
      const [left, top, right, bottom] = view.map(value => Math.floor(value / 64));
      for (let x = left; x <= right; x++) for (let y = top; y <= bottom; y++) {
        for (const item of this.cells.get(`${x},${y}`) || []) if (overlaps(item.bounds, view)) found.add(item);
      }
      return [...found];
    }
  }

  function distanceToSegment(point, a, b) {
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const fraction = dx || dy ? Math.max(0, Math.min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / (dx * dx + dy * dy))) : 0;
    return Math.hypot(point[0] - a[0] - fraction * dx, point[1] - a[1] - fraction * dy);
  }

  class StreetLayer {
    constructor({ features, background, project, root, labels, highlight, onSelect, onHover }) {
      this.root = root;
      this.labelRoot = labels;
      this.highlightRoot = highlight;
      this.onSelect = onSelect;
      this.onHover = onHover;
      this.items = new Map(features.map(feature => {
        const parts = feature.geometry.coordinates.map(part => part.map(project));
        const points = parts.flat();
        return [feature.id, { feature, parts, bounds: bounds(points), anchor: project(feature.anchor),
          d: parts.map(part => part.map((point, index) => `${index ? "L" : "M"}${point[0].toFixed(3)},${point[1].toFixed(3)}`).join("")).join("") }];
      }));
      this.background = background.map(part => {
        const points = part.map(project);
        return { bounds: bounds(points), d: points.map((point, index) => `${index ? "L" : "M"}${point[0].toFixed(3)},${point[1].toFixed(3)}`).join("") };
      });
      this.itemIndex = new SpatialIndex(this.items.values());
      this.backgroundIndex = new SpatialIndex(this.background);
      this.paths = new Map();
      this.labels = new Map();
      this.visible = [];
      this.lastCandidates = [];
      this.backgroundPath = node("path", { class: "street-background", "aria-hidden": "true" });
      root.append(this.backgroundPath);
      this.highlightPath = node("path", { class: "street-highlight", "aria-hidden": "true", "pointer-events": "none" });
      this.solutionHalo = node("path", { class: "street-solution-halo", "aria-hidden": "true" });
      this.solutionPath = node("path", { class: "street-solution", "aria-hidden": "true" });
      highlight.append(this.highlightPath, this.solutionHalo, this.solutionPath);
    }

    render(options) {
      this.options = options;
      this.root.style.display = options.visible ? "" : "none";
      this.labelRoot.style.display = options.visible ? "" : "none";
      this.highlightRoot.style.display = options.visible ? "" : "none";
      document.getElementById("map-content").classList.toggle("has-street-solution", Boolean(options.visible && options.correctId));
      const solution = this.items.get(options.correctId);
      this.solutionHalo.setAttribute("d", solution?.d || "");
      this.solutionPath.setAttribute("d", solution?.d || "");
      this.solutionPath.dataset.id = options.correctId || "";
      if (!options.visible) { this.visible = []; return; }
      const inverse = options.matrix.inverse();
      const cornerA = new DOMPoint(options.viewport.left, options.viewport.top).matrixTransform(inverse);
      const cornerB = new DOMPoint(options.viewport.right, options.viewport.bottom).matrixTransform(inverse);
      const view = [cornerA.x, cornerA.y, cornerB.x, cornerB.y];
      const detail = options.zoom >= 5;
      const visible = this.itemIndex.query(view).filter(item => detail || item.feature.category !== "local" || (options.focusPool && options.pool.has(item.feature.id)) || item.feature.id === options.correctId);
      visible.sort((a, b) => Number(options.pool.has(b.feature.id)) - Number(options.pool.has(a.feature.id))
        || ({ major: 0, secondary: 1, local: 2, unclassified: 3 }[a.feature.category] - { major: 0, secondary: 1, local: 2, unclassified: 3 }[b.feature.category]));
      this.visible = visible.slice(0, 1600);
      const ids = new Set(this.visible.map(item => item.feature.id));
      for (const id of [options.correctId, options.wrongId]) {
        const item = this.items.get(id);
        if (item && overlaps(item.bounds, view) && !ids.has(id)) { this.visible.push(item); ids.add(id); }
      }
      for (const [id, path] of this.paths) if (!ids.has(id)) { path.remove(); this.paths.delete(id); }
      this.backgroundPath.setAttribute("d", options.zoom >= 7 ? this.backgroundIndex.query(view).map(item => item.d).join("") : "");
      for (const item of this.visible) {
        const { feature } = item;
        let path = this.paths.get(feature.id);
        if (!path) {
          path = node("path", { d: item.d, "data-id": feature.id, "data-anchor-x": item.anchor[0], "data-anchor-y": item.anchor[1], role: "button" });
          path.addEventListener("focus", () => this.onHover(feature.id));
          path.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") { event.preventDefault(); this.onSelect(feature.id); }
          });
          this.root.append(path);
          this.paths.set(feature.id, path);
        }
        const active = options.pool.has(feature.id) && !options.revealed;
        path.setAttribute("class", `street-shape street-${feature.category}${options.pool.has(feature.id) ? "" : " is-context"}${feature.id === options.correctId ? " is-correct" : ""}${feature.id === options.wrongId ? " is-wrong" : ""}`);
        path.setAttribute("tabindex", active ? "0" : "-1");
        path.setAttribute("aria-disabled", String(!active));
        path.setAttribute("aria-label", options.inSession && !options.revealed ? t("m203") : feature.nameEn ? `${feature.nameZh} · ${feature.nameEn}` : feature.nameZh);
      }
      this.renderLabels(view);
      this.setHighlight(options.highlightId);
      document.getElementById("street-map-hint").textContent = options.focusPool ? t("m204", options.pool.size) : !detail ? t("m205")
        : visible.length > 1600 ? t("m206") : t("m207");
    }

    renderLabels(view) {
      const options = this.options;
      const occupied = [];
      const shown = new Set();
      if (options.names && options.zoom >= 3) {
        const normalize = value => value.normalize("NFKC").replaceAll("臺", "台").replace(/\s/g, "");
        const candidates = this.visible.filter(item => (!options.focusPool || options.pool.has(item.feature.id)) && item.feature.id !== options.hiddenId
          && (!options.hiddenPrefix || !normalize(item.feature.nameZh).includes(normalize(options.hiddenPrefix)))
          && overlaps([item.anchor[0], item.anchor[1], item.anchor[0], item.anchor[1]], view));
        for (const item of candidates) {
          if (shown.size >= 65) break;
          const feature = item.feature;
          const name = options.language === "en" ? feature.nameEn : feature.nameZh;
          if (!name) continue;
          const point = new DOMPoint(...item.anchor).matrixTransform(options.matrix);
          const english = options.language === "en";
          const hasSecondary = options.language === "both" && feature.nameEn;
          const displayName = name.length > 52 ? name.slice(0, 51) + "…" : name;
          const secondaryName = hasSecondary ? feature.nameEn.length > 58 ? feature.nameEn.slice(0, 57) + "…" : feature.nameEn : "";
          const width = Math.max(displayName.length * (english ? 5.4 : 10.5), secondaryName.length * 4.2) + 8;
          const box = [point.x - width / 2, point.y - 15, point.x + width / 2, point.y + (hasSecondary ? 15 : 5)];
          if (occupied.some(other => overlaps(box, other))) continue;
          let label = this.labels.get(feature.id);
          if (!label) {
            const group = node("g", { class: "street-label", "data-id": feature.id, "aria-hidden": "true" });
            const main = node("text", { class: "street-label-main" });
            const secondary = node("text", { class: "street-label-secondary" });
            group.append(main, secondary);
            label = { group, main, secondary };
            this.labels.set(feature.id, label);
            this.labelRoot.append(group);
          }
          const scale = Math.hypot(options.matrix.a, options.matrix.b);
          label.group.setAttribute("transform", `translate(${item.anchor[0]},${item.anchor[1]})`);
          label.group.style.strokeWidth = `${2.5 / scale}px`;
          label.main.textContent = displayName;
          label.main.setAttribute("lang", english ? "en" : "zh-Hant");
          label.main.style.fontSize = `${11 / scale}px`;
          label.main.setAttribute("y", -2 / scale);
          label.secondary.textContent = secondaryName;
          label.secondary.style.fontSize = `${8 / scale}px`;
          label.secondary.setAttribute("y", 11 / scale);
          shown.add(feature.id);
          occupied.push(box);
        }
      }
      for (const [id, label] of this.labels) label.group.style.display = shown.has(id) ? "" : "none";
    }

    setHighlight(id) {
      const item = this.items.get(id);
      this.highlightPath.setAttribute("d", item && this.options?.visible ? item.d : "");
      this.highlightPath.dataset.id = item ? id : "";
    }

    pick(clientX, clientY, touch = false, preferred = null) {
      const options = this.options;
      if (!options?.visible || options.revealed) return null;
      const matrix = this.root.getScreenCTM();
      if (!matrix) return null;
      const position = new DOMPoint(clientX, clientY).matrixTransform(matrix.inverse());
      const point = [position.x, position.y];
      const scale = Math.hypot(matrix.a, matrix.b);
      const tolerance = (touch ? 30 : 9) / scale;
      const nearby = [point[0] - tolerance, point[1] - tolerance, point[0] + tolerance, point[1] + tolerance];
      const hits = [];
      for (const item of this.visible) {
        if (!options.pool.has(item.feature.id) || !overlaps(item.bounds, nearby)) continue;
        let distance = Infinity;
        for (const part of item.parts) for (let index = 1; index < part.length; index++) distance = Math.min(distance, distanceToSegment(point, part[index - 1], part[index]));
        if (distance <= tolerance) hits.push({ id: item.feature.id, distance });
      }
      hits.sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id));
      this.lastCandidates = hits.slice(0, 6).map(hit => hit.id);
      if (preferred && hits.some(hit => hit.id === preferred && hit.distance <= (hits[0]?.distance || 0) + 1 / scale)) return preferred;
      return hits[0]?.id || null;
    }
  }

  window.TaipeiStreetLayer = StreetLayer;
})();
