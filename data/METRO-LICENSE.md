# Metro-Geodaten: Open Database License 1.0

The files `metro.js`, `metro-routes-source.geojson` and `metro-extra-source/*.json` contain information from
OpenStreetMap, which is made available here under the Open Database License
(ODbL) version 1.0.

© OpenStreetMap contributors

- Attribution: https://www.openstreetmap.org/copyright
- ODbL 1.0 text: https://opendatacommons.org/licenses/odbl/1-0/

The geographic database and modifications to it are offered under ODbL 1.0.
No additional restrictions are imposed on the use of these data.

## Source and changes

The original GeoJSON is included in full as `metro-routes-source.geojson`.
It was obtained from:

https://github.com/davidyen1124/mrt-app/blob/32a31120995022944ef4c59cf0484ce15b22bccc/data/taipei_lines.geo.json

Source snapshot generated: 2026-09-27T21:31:37.540Z.
SHA-256: `8a6a247284c5db5e91369db341e22d54798f9e1f826a8ac328b80ce9ae94da93`.

The source identifies its geometry as OpenStreetMap data under ODbL 1.0.
`metro.js` includes all nine routes from this source and adds geographically
separate route geometries for Airport MRT A, Danhai V, Ankeng K and Sanying LB.
The additional files are preserved in `metro-extra-source/` and were obtained
from this fixed version of a repository that explicitly licenses its data under ODbL:

https://github.com/rareone0602/taipei-mrt-minecraft/tree/aaaa1d71ce30ebb4371c13ed83f6e199a2e8cfcd/data/lines

The upstream data licence is documented here:
https://github.com/rareone0602/taipei-mrt-minecraft/blob/aaaa1d71ce30ebb4371c13ed83f6e199a2e8cfcd/LICENSE-DATA

OSM timestamps and SHA-256 hashes for each additional file are recorded in
`metro.js`. Unique route-way geometries were extracted without changing their
coordinates. Inactive and non-track members were excluded. Disconnected ways
remain disconnected; no invented connecting segments were added. Names,
colours and source metadata were added. Airport MRT uses a darker purple for
legibility. The display is clipped to Taipei City and New Taipei City.

These files contain geographic data, not application code from the upstream
project. The district polygons are a separate CC0 dataset documented in
`THIRD_PARTY_NOTICES.md`. This notice does not assign a licence to this app's
own source code or to unrelated files.
