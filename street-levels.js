/* Deterministic ten-street curricula; shared by both learning regions. */
(() => {
  "use strict";
  const SIZE = 10;
  function areaKey(ids) { return "whole-v1|" + [...ids].sort().join("|"); }
  function rank(features, data, ids, allIds, cities = []) {
    const selected = new Set(ids);
    const wholeRegion = selected.size === allIds.length && allIds.every(id => selected.has(id));
    const city = cities.find(city => city.ids.length === selected.size && city.ids.every(id => selected.has(id)));
    function score(feature) {
      const metric = data.streets[feature.id];
      if (!metric) return 0;
      if (wholeRegion) return metric.length;
      if (city && metric.cities[city.id] !== undefined) return metric.cities[city.id];
      return [...selected].reduce((sum, id) => sum + (metric.districts[id] || 0), 0);
    }
    return features.map(feature => ({ feature, length: score(feature) })).sort((a,b) => b.length - a.length || (a.feature.id < b.feature.id ? -1 : a.feature.id > b.feature.id ? 1 : 0));
  }
  function slice(ranked, requested, review = false) {
    const total = Math.ceil(ranked.length / SIZE);
    const level = Math.min(Math.max(1, Math.trunc(requested) || 1), Math.max(1, total));
    return { level, total, fresh: ranked.slice((level - 1) * SIZE, level * SIZE), active: ranked.slice(review ? 0 : (level - 1) * SIZE, level * SIZE) };
  }
  window.StreetLevels = { SIZE, areaKey, rank, slice };
})();
