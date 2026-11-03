"""Functional browser tests. Development-only dependency: Playwright."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import shutil
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_KEY = "taipei-kennen.progress.v1"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = partial(QuietHandler, directory=str(ROOT))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("TAIPEI_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome")
        cls.browser = cls.playwright.chromium.launch(executable_path=executable, headless=True, args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1100})
        self.page = self.context.new_page()
        self.errors = []
        self.external_requests = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.external_requests.append(request.url)
                     if request.url.startswith(("https://", "http://")) and not request.url.startswith(self.url) else None)
        self.page.goto(self.url + "?region=taipei")
        self.page.wait_for_selector('body[data-ready="true"]', state="attached")
        self.open_practice()
        self.page.wait_for_selector(".district-shape")
        self.features = self.page.evaluate("window.TAIPEI_DATA.features.map(({id,nameZh,nameEn,cityId}) => ({id,nameZh,nameEn,cityId}))")
        self.rivers = self.page.evaluate("window.TAIPEI_RIVERS.features.map(({id,nameZh,nameEn,kind,cityIds}) => ({id,nameZh,nameEn,kind,cityIds}))")

    def tearDown(self):
        self.assertEqual(self.errors, [], "JavaScript errors")
        self.assertEqual(self.external_requests, [], "Unexpected external network requests")
        self.context.close()

    def open_practice(self):
        if self.page.locator("#home-view").is_visible():
            if self.page.locator("#menu-toggle").is_visible():
                self.page.locator("#menu-toggle").click()
            self.page.locator('[data-nav="explore"]').click()

    def choose(self, ids):
        for item in self.page.locator("#district-picker input").all():
            item.set_checked(item.get_attribute("value") in ids)

    def click_district(self, id):
        position = self.page.locator(f'.district-shape[data-id="{id}"]').evaluate("""el => {
            const point = new DOMPoint(Number(el.dataset.anchorX), Number(el.dataset.anchorY));
            const position = point.matrixTransform(el.getScreenCTM());
            return {x:position.x, y:position.y};
        }""")
        self.page.mouse.click(position["x"], position["y"])

    def target(self):
        name = self.page.locator("#question-name").inner_text()
        return next(feature for feature in self.features + self.rivers if name in [feature["nameZh"], feature["nameEn"]])

    def click_river(self, id):
        point = self.page.locator(f'.river-hit[data-id="{id}"]').evaluate("""el => {
            const p = new DOMPoint(Number(el.dataset.anchorX), Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        inside = self.page.locator(f'.river-shape[data-id="{id}"]').evaluate("""(el, point) =>
            el.isPointInFill(new DOMPoint(point.x,point.y).matrixTransform(el.getScreenCTM().inverse()))""", point)
        self.assertTrue(inside, "River anchor must lie inside its real water area")
        self.page.mouse.click(point["x"], point["y"])

    def test_river_overlay_names_and_preferences(self):
        self.assertEqual(self.page.locator(".river-shape").count(), 4)
        self.assertFalse(self.page.locator("#include-rivers").is_checked())
        self.assertTrue(self.page.locator("#river-layer").is_visible())
        self.assertGreater(self.page.locator(".river-label:visible").count(), 0)
        self.page.locator("#show-rivers").uncheck()
        self.assertFalse(self.page.locator("#river-layer").is_visible())
        self.assertEqual(self.page.locator(".river-label:visible").count(), 0)
        self.assertTrue(self.page.locator("#show-river-labels").is_disabled())
        self.page.locator("#show-rivers").check()
        self.page.locator("#language").select_option("en")
        self.assertEqual(self.page.locator(".river-label .zh:visible").count(), 0)
        self.page.locator("#include-rivers").check()
        for river in self.rivers:
            self.click_river(river["id"])
            self.assertIn(river["nameEn"], self.page.locator("#map-detail").inner_text())
        self.page.locator("#show-river-labels").uncheck()
        self.assertEqual(self.page.locator(".river-label:visible").count(), 0)
        self.assertGreater(self.page.locator(".district-label:visible").count(), 0)
        self.page.reload()
        self.assertTrue(self.page.locator("#include-rivers").is_checked())
        self.assertFalse(self.page.locator("#show-river-labels").is_checked())
        self.assertEqual(self.page.locator("#river-picker input:checked").count(), 4)
        self.assertIsNone(self.progress())

    def test_river_only_quiz_scoring_retry_and_persistence(self):
        self.page.locator("#include-rivers").check()
        self.page.locator("#select-all").click()
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#round-size").select_option("all")
        self.assertIn("4 Aufgaben", self.page.locator("#start-button").inner_text())
        self.page.locator("#start-button").click()
        visited = set()
        first_error = None
        for number in range(4):
            target = self.target()
            self.assertEqual(target["kind"], "river")
            visited.add(target["id"])
            self.assertIn("diesen Fluss", self.page.locator("#question-instruction").inner_text())
            self.assertFalse(self.page.locator(f'.river-label[data-id="{target["id"]}"]').is_visible())
            self.assertTrue(self.page.locator("#show-rivers").is_disabled())
            self.page.locator('.district-shape[data-id="neihu"]').dispatch_event("keydown", {"key": "Enter"})
            self.assertFalse(self.page.locator("#feedback").is_visible())
            chosen = target["id"]
            if number == 0:
                first_error = target["id"]
                chosen = next(river["id"] for river in self.rivers if river["id"] != first_error)
            self.click_river(chosen)
            self.assertTrue(self.page.locator(f'.river-shape[data-id="{target["id"]}"]').evaluate("el => el.classList.contains('is-correct')"))
            self.page.locator("#next-button").click()
        self.assertEqual(visited, {river["id"] for river in self.rivers})
        self.assertIn("3 / 4", self.page.locator("#result-score").inner_text())
        self.page.locator("#retry-errors").click()
        self.assertEqual(self.target()["id"], first_error)
        self.click_river(first_error)
        self.page.locator("#next-button").click()
        self.assertEqual(self.progress()["rounds"], 2)
        self.assertEqual(self.progress()["districts"][first_error], {"attempts": 2, "correct": 1})
        self.page.reload()
        self.assertEqual(sum(stats["attempts"] for stats in self.progress()["districts"].values()), 5)
        self.page.locator("#include-rivers").uncheck()
        self.page.locator("#progress-open").click()
        self.assertIn("Flüsse", self.page.locator("#progress-list").inner_text())

    def test_river_confluence_prefers_water_over_neighbour_hit_padding(self):
        self.page.locator("#include-rivers").check()
        point = self.page.evaluate("""() => {
            const references = ['neihu','wenshan'].map(id => {
                const feature = window.TAIPEI_DATA.features.find(f => f.id === id);
                const el = document.querySelector(`.district-shape[data-id="${id}"]`);
                const pixel = new DOMPoint(Number(el.dataset.anchorX),Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
                return {anchor:feature.anchor,pixel};
            });
            const [a,b] = references;
            const latitude = lat => Math.log(Math.tan(Math.PI/4+lat*Math.PI/360));
            return {x:a.pixel.x+(121.465125-a.anchor[0])/(b.anchor[0]-a.anchor[0])*(b.pixel.x-a.pixel.x),
                    y:a.pixel.y+(latitude(25.105501)-latitude(a.anchor[1]))/(latitude(b.anchor[1])-latitude(a.anchor[1]))*(b.pixel.y-a.pixel.y)};
        }""")
        inside = self.page.locator('.river-shape[data-id="river-tamsui"]').evaluate("""(el, p) =>
            el.isPointInFill(new DOMPoint(p.x,p.y).matrixTransform(el.getScreenCTM().inverse()))""", point)
        self.assertTrue(inside)
        self.assertEqual(self.page.evaluate("p => document.elementFromPoint(p.x,p.y)?.dataset.id", point), "river-keelung")
        self.page.mouse.click(point["x"], point["y"])
        self.assertIn("Tamsui River", self.page.locator("#map-detail").inner_text())

    def test_touch_river_quiz_pan_pinch_and_tap(self):
        self.context.close()
        self.context = self.browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.external_requests.append(request.url)
                     if request.url.startswith(("https://", "http://")) and not request.url.startswith(self.url) else None)
        self.page.goto(self.url + "?region=taipei")
        self.open_practice()
        self.page.locator("#include-rivers").check()
        self.page.locator("#select-all").click()
        for item in self.page.locator("#river-picker input").all():
            item.set_checked(item.get_attribute("value") == "river-keelung")
        self.page.locator('[data-mode="quiz"]').tap()
        self.page.locator("#start-button").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        client = self.context.new_cdp_session(self.page)

        def touches(kind, points):
            client.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [
                {"id": id, "x": x, "y": y} for id, x, y in points]})
            self.page.wait_for_timeout(60)

        box = self.page.locator("#taipei-map").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        touches("touchStart", [(1,cx-45,cy),(2,cx+45,cy)])
        touches("touchMove", [(1,cx-85,cy),(2,cx+85,cy)])
        touches("touchEnd", [])
        touches("touchStart", [(1,cx,cy)])
        touches("touchMove", [(1,cx+25,cy+20)])
        touches("touchEnd", [])
        self.assertIsNone(self.progress())
        self.assertFalse(self.page.locator("#feedback").is_visible())
        self.page.locator("#zoom-reset").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        point = self.page.locator('.river-hit[data-id="river-keelung"]').evaluate("""el => {
            const p = new DOMPoint(Number(el.dataset.anchorX),Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        touches("touchStart", [(1,point["x"],point["y"])])
        touches("touchEnd", [])
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"]["river-keelung"], {"attempts": 1, "correct": 1})
        self.assertFalse(self.page.evaluate("document.documentElement.scrollWidth > innerWidth"))

    def test_mixed_river_quiz_scope_selection_and_cards(self):
        self.page.locator("#city-scope").select_option("taipei")
        self.page.locator("#include-rivers").check()
        self.assertEqual(self.page.locator("#river-picker input").count(), 3)
        self.assertEqual(self.page.locator('#river-picker input[value="river-dahan"]').count(), 0)
        self.choose(["neihu"])
        self.page.locator('#river-picker input[value="river-keelung"]').uncheck()
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#round-size").select_option("all")
        self.assertIn("3 Aufgaben", self.page.locator("#start-button").inner_text())
        self.page.locator("#start-button").click()
        visited = set()
        for _ in range(3):
            target = self.target()
            visited.add(target["id"])
            if target.get("kind") == "river":
                self.click_river(target["id"])
            else:
                self.page.locator('.river-hit[data-id="river-tamsui"]').dispatch_event("keydown", {"key": "Enter"})
                self.assertFalse(self.page.locator("#feedback").is_visible())
                self.click_district(target["id"])
            self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
            self.page.locator("#next-button").click()
        self.assertEqual(visited, {"neihu", "river-tamsui", "river-xindian"})
        self.page.locator("#back-to-setup").click()
        self.page.locator("#city-scope").select_option("new-taipei")
        self.assertEqual(self.page.locator("#river-picker input").count(), 4)
        self.page.locator("#select-all").click()
        for item in self.page.locator("#river-picker input").all():
            item.set_checked(item.get_attribute("value") == "river-dahan")
        self.page.reload()
        self.assertEqual(self.page.locator("#river-picker input:checked").count(), 1)
        self.page.locator('[data-mode="cards"]').click()
        self.page.locator("#start-button").click()
        before = self.progress()
        self.assertEqual(self.target()["id"], "river-dahan")
        self.page.locator("#reveal-button").click()
        self.assertIn("大漢溪", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress(), before, "River learning cards must not count as quiz attempts")
        self.page.locator("#next-button").click()
        self.assertIn("1 Karten", self.page.locator("#result-score").inner_text())

    def progress(self):
        return self.page.evaluate("key => JSON.parse(localStorage.getItem(key) || 'null')", PROGRESS_KEY)

    def test_map_exploration_zoom_and_labels(self):
        self.assertEqual(self.page.locator(".district-shape").count(), 41)
        for feature in self.features:
            self.click_district(feature["id"])
            self.assertIn(feature["nameZh"], self.page.locator("#map-detail").inner_text())
        before = self.page.locator("#map-content").get_attribute("transform")
        self.page.locator("#zoom-in").click()
        self.assertNotEqual(before, self.page.locator("#map-content").get_attribute("transform"))
        self.page.locator("#zoom-reset").click()
        self.assertEqual(before, self.page.locator("#map-content").get_attribute("transform"))
        self.page.locator("#language").select_option("en")
        self.click_district("neihu")
        self.assertIn("Neihu Dist.", self.page.locator("#map-detail").inner_text())
        self.assertNotIn("內湖區", self.page.locator("#map-detail").inner_text())
        self.page.locator("#show-labels-taipei").uncheck()
        self.page.locator("#show-labels-new-taipei").uncheck()
        self.assertEqual(self.page.locator(".district-label:visible").count(), 0)
        self.assertIsNone(self.progress())

    def test_city_labels_are_independent_of_quiz_scope(self):
        self.page.locator("#city-scope").select_option("taipei")
        self.page.locator("#show-labels-taipei").uncheck()
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()

        def visible_cities():
            return self.page.locator(".district-label:visible").evaluate_all("""labels => labels.map(label =>
                window.TAIPEI_DATA.features.find(feature => feature.id === label.dataset.id).cityId)""")

        self.assertTrue(visible_cities(), "New Taipei labels must remain visible around the Taipei quiz")
        self.assertEqual(set(visible_cities()), {"new-taipei"})
        target = self.target()
        target_label = self.page.locator(f'.district-label[data-id="{target["id"]}"]')
        self.assertFalse(target_label.is_visible())
        context = self.page.locator('.district-shape[data-id="nt-sanchong"]')
        self.assertEqual(context.get_attribute("aria-disabled"), "true")
        self.click_district("nt-sanchong")
        self.assertIsNone(self.progress(), "Context districts must not submit quiz answers")
        transform = self.page.locator("#map-content").get_attribute("transform")
        self.page.locator("#show-labels-new-taipei").uncheck()
        self.assertEqual(self.page.locator(".district-label:visible").count(), 0)
        self.page.locator("#show-labels-new-taipei").check()
        self.assertTrue(visible_cities())
        self.page.locator("#show-labels-taipei").check()
        self.assertFalse(target_label.is_visible(), "Enabling city labels must not reveal the target")
        self.page.locator("#show-labels-taipei").uncheck()
        self.assertEqual(transform, self.page.locator("#map-content").get_attribute("transform"))
        self.assertIsNone(self.progress())
        self.click_district(target["id"])
        self.page.locator("#next-button").click()
        self.assertEqual(set(visible_cities()), {"new-taipei"})

        self.page.reload()
        self.assertFalse(self.page.locator("#show-labels-taipei").is_checked())
        self.assertTrue(self.page.locator("#show-labels-new-taipei").is_checked())
        self.assertEqual(self.progress()["districts"][target["id"]]["attempts"], 1)
        self.page.locator("#city-scope").select_option("new-taipei")
        self.page.locator("#show-labels-taipei").check()
        self.page.locator("#show-labels-new-taipei").uncheck()
        self.page.locator("#start-button").click()
        self.assertNotIn("new-taipei", visible_cities())
        self.page.locator("#show-labels-new-taipei").check()
        self.assertFalse(self.page.locator(f'.district-label[data-id="{self.target()["id"]}"]').is_visible())

    def test_metro_layer_toggle_persistence_and_language(self):
        self.assertTrue(self.page.locator("#show-metro").is_checked())
        self.assertEqual(self.page.locator(".metro-line").count(), 13)
        self.assertEqual(self.page.locator(".metro-chip").count(), 12)
        self.assertTrue(self.page.locator("#metro-credit").is_visible())
        self.assertEqual(self.page.locator('.metro-line[data-line="BR"]').evaluate("el => getComputedStyle(el).stroke"), "rgb(196, 140, 49)")
        self.page.locator("#zoom-in").click()
        line_matrix = self.page.locator(".metro-line").first.evaluate("el => { const m=el.getScreenCTM(); return [m.a,m.d,m.e,m.f]; }")
        district_matrix = self.page.locator(".district-shape").first.evaluate("el => { const m=el.getScreenCTM(); return [m.a,m.d,m.e,m.f]; }")
        self.assertEqual(line_matrix, district_matrix)
        before = self.page.locator("#map-content").get_attribute("transform")
        self.page.locator("#show-metro").uncheck()
        self.assertEqual(before, self.page.locator("#map-content").get_attribute("transform"))
        self.assertFalse(self.page.locator("#metro-layer").is_visible())
        self.assertFalse(self.page.locator("#metro-legend").is_visible())
        self.page.reload()
        self.assertFalse(self.page.locator("#show-metro").is_checked())
        self.assertFalse(self.page.locator("#metro-layer").is_visible())
        self.page.locator("#show-metro").check()
        self.assertTrue(self.page.locator("#metro-layer").is_visible())
        self.page.locator("#metro-legend summary").click()
        self.page.locator("#language").select_option("zh")
        self.assertEqual(self.page.locator('.metro-chip[data-line="BR"] .metro-name').inner_text(), "文湖線")
        self.page.locator("#language").select_option("en")
        self.assertEqual(self.page.locator('.metro-chip[data-line="BR"] .metro-name').inner_text(), "Wenhu")
        self.assertIsNone(self.progress())

    def test_metro_track_is_geographically_aligned_and_clicks_reach_district(self):
        self.choose(["nangang"])
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        point = self.page.locator('.metro-line[data-line="BR"]').evaluate("""el => {
            const p = el.getPointAtLength(0).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        hit = self.page.evaluate("p => document.elementFromPoint(p.x,p.y)?.closest('.district-shape')?.dataset.id", point)
        self.assertEqual(hit, "nangang", "The Wenhu terminus must align with the Nangang district and allow clicks through the line")
        self.assertIsNone(self.progress())
        self.page.mouse.click(point["x"], point["y"])
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"]["nangang"]["attempts"], 1)

    def test_zoom_out_from_initial_view_and_restore(self):
        district = self.page.locator('.district-shape[data-id="neihu"]')
        initial_width = district.bounding_box()["width"]
        self.page.locator("#zoom-out").click(timeout=1500)
        self.assertLess(district.bounding_box()["width"], initial_width * 0.9)
        self.page.locator("#zoom-reset").click()
        self.assertAlmostEqual(district.bounding_box()["width"], initial_width, delta=1)
        self.assertEqual(self.page.locator("#zoom-level").inner_text(), "100 %")
        slider = self.page.locator("#zoom-range")
        slider.focus()
        slider.press("Home")
        self.assertEqual(self.page.locator("#zoom-level").inner_text(), "50 %")
        self.assertLess(district.bounding_box()["width"], initial_width * 0.55)
        self.assertTrue(self.page.locator("#zoom-out").is_disabled())
        slider.press("End")
        self.assertEqual(self.page.locator("#zoom-level").inner_text(), "1200 %")
        self.assertGreater(district.bounding_box()["width"], initial_width * 11)
        self.assertTrue(self.page.locator("#zoom-in").is_disabled())
        self.page.locator("#zoom-reset").click()
        self.assertEqual(self.page.locator("#zoom-level").inner_text(), "100 %")

    def test_wheel_zoom_preserves_pointer_position_and_ignores_horizontal_scroll(self):
        district = self.page.locator('.district-shape[data-id="neihu"]')
        anchor = """el => {
            const p = new DOMPoint(Number(el.dataset.anchorX), Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }"""
        point = district.evaluate(anchor)
        initial_width = district.bounding_box()["width"]
        initial_scroll = self.page.evaluate("scrollY")
        self.page.mouse.move(point["x"], point["y"])
        self.page.mouse.wheel(0, -240)
        self.page.wait_for_function("width => document.querySelector('[data-id=neihu].district-shape').getBoundingClientRect().width > width * 1.2", arg=initial_width)

        after = district.evaluate(anchor)
        self.assertAlmostEqual(after["x"], point["x"], delta=1)
        self.assertAlmostEqual(after["y"], point["y"], delta=1)
        self.assertEqual(self.page.evaluate("scrollY"), initial_scroll)
        transform = self.page.locator("#map-content").get_attribute("transform")
        self.page.mouse.wheel(160, 0)
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.locator("#map-content").get_attribute("transform"), transform)
        self.page.mouse.wheel(0, 240)
        self.page.wait_for_function("width => document.querySelector('[data-id=neihu].district-shape').getBoundingClientRect().width < width * 1.05", arg=initial_width)
        controls = self.page.locator("#zoom-in").bounding_box()
        self.page.mouse.move(controls["x"] + controls["width"] / 2, controls["y"] + controls["height"] / 2)
        self.page.mouse.wheel(0, -120)
        self.page.wait_for_function("width => document.querySelector('[data-id=neihu].district-shape').getBoundingClientRect().width > width * 1.2", arg=initial_width)

    def test_touch_pinch_pan_and_tap_do_not_confuse_quiz_answers(self):
        self.context.close()
        self.context = self.browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.external_requests.append(request.url)
                     if request.url.startswith(("https://", "http://")) and not request.url.startswith(self.url) else None)
        self.page.goto(self.url + "?region=taipei")
        self.open_practice()
        self.page.locator('[data-mode="quiz"]').tap()
        self.page.locator("#start-button").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        self.assertTrue(self.page.locator("#metro-credit").is_visible())
        self.assertFalse(self.page.evaluate("document.documentElement.scrollWidth > innerWidth"))
        client = self.context.new_cdp_session(self.page)

        def touches(kind, points):
            client.send("Input.dispatchTouchEvent", {
                "type": kind,
                "touchPoints": [{"id": id, "x": x, "y": y, "radiusX": 2, "radiusY": 2, "force": 1} for id, x, y in points]
            })

        district = self.page.locator('.district-shape[data-id="neihu"]')
        initial_width = district.bounding_box()["width"]
        box = self.page.locator("#taipei-map").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        touches("touchStart", [(1, cx - 22, cy)])
        touches("touchStart", [(1, cx - 22, cy), (2, cx + 22, cy)])
        for distance in [30, 40, 50, 60, 70]:
            touches("touchMove", [(1, cx - distance, cy), (2, cx + distance, cy)])
        touches("touchEnd", [(1, cx - 70, cy)])
        touches("touchMove", [(1, cx - 50, cy + 10)])
        touches("touchEnd", [])
        self.assertGreater(district.bounding_box()["width"], initial_width * 2)
        self.assertFalse(self.page.locator("#feedback").is_visible())
        self.assertIsNone(self.progress())

        self.page.locator("#zoom-reset").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        box = self.page.locator("#taipei-map").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        touches("touchStart", [(1, cx - 60, cy)])
        touches("touchStart", [(1, cx - 60, cy), (2, cx + 60, cy)])
        touches("touchMove", [(1, cx - 30, cy), (2, cx + 30, cy)])
        touches("touchEnd", [])
        self.assertLess(district.bounding_box()["width"], initial_width * 0.6)
        self.assertFalse(self.page.locator("#feedback").is_visible())
        self.assertIsNone(self.progress())

        self.page.locator("#zoom-reset").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        box = self.page.locator("#taipei-map").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        before = self.page.locator("#map-content").get_attribute("transform")
        touches("touchStart", [(1, cx, cy)])
        touches("touchMove", [(1, cx + 35, cy + 15)])
        touches("touchEnd", [])
        self.assertNotEqual(self.page.locator("#map-content").get_attribute("transform"), before)
        self.assertIsNone(self.progress())
        touches("touchStart", [(1, cx, cy)])
        touches("touchCancel", [])
        self.assertIsNone(self.progress())

        self.page.locator("#zoom-reset").tap()
        target = self.target()
        point = self.page.locator(f'.district-shape[data-id="{target["id"]}"]').evaluate("""el => {
            const p = new DOMPoint(Number(el.dataset.anchorX), Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        touches("touchStart", [(1, point["x"], point["y"])])
        touches("touchEnd", [])
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(sum(row["attempts"] for row in self.progress()["districts"].values()), 1)

    def test_quiz_scoring_repeat_persistence_and_delete(self):
        ids = ["neihu", "nangang", "daan"]
        self.choose(ids)
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        self.assertIn("1 / 3", self.page.locator("#session-count").inner_text())
        first = self.target()
        self.assertFalse(self.page.locator(f'.district-label[data-id="{first["id"]}"]').is_visible())
        self.assertEqual(self.page.locator(f'.district-shape[data-id="{first["id"]}"]').get_attribute("aria-label"), "Bezirk auf der Karte auswählen")
        wrong = next(id for id in ids if id != first["id"])
        self.click_district(wrong)
        self.assertTrue(self.page.locator("#feedback.wrong").is_visible())
        self.assertEqual(self.page.locator(".district-shape.is-correct").get_attribute("data-id"), first["id"])
        self.assertEqual(self.page.locator(".district-shape.is-wrong").get_attribute("data-id"), wrong)
        self.click_district(first["id"])
        self.assertEqual(sum(row["attempts"] for row in self.progress()["districts"].values()), 1)
        self.page.locator("#next-button").click()
        self.click_district(self.target()["id"])
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.page.locator("#next-button").click()
        self.page.locator("#reveal-button").click()
        self.page.locator("#next-button").click()
        self.assertIn("1 / 3", self.page.locator("#result-score").inner_text())
        self.assertEqual(self.page.locator(".result-row.wrong").count(), 2)
        self.page.locator("#retry-errors").click()
        self.assertIn("1 / 2", self.page.locator("#session-count").inner_text())
        for _ in range(2):
            self.click_district(self.target()["id"])
            self.page.locator("#next-button").click()
        self.assertIn("2 / 2", self.page.locator("#result-score").inner_text())
        self.assertFalse(self.page.locator("#retry-errors").is_visible())
        stats = self.progress()
        self.assertEqual(stats["rounds"], 2)
        self.assertEqual(sum(row["attempts"] for row in stats["districts"].values()), 5)
        self.assertEqual(sum(row["correct"] for row in stats["districts"].values()), 3)
        self.page.reload()
        self.assertEqual(self.progress(), stats)
        self.page.locator("#progress-open").click()
        self.assertIn("5 beantwortete Aufgaben", self.page.locator("#progress-summary").inner_text())
        self.page.locator("#delete-progress").click()
        self.page.locator("#delete-cancel").click()
        self.assertEqual(self.progress(), stats)
        self.page.locator("#delete-progress").click()
        self.page.locator("#delete-confirm").click()
        self.assertIsNone(self.progress())
        self.page.reload()
        self.page.locator("#progress-open").click()
        self.assertIn("ersten Quizantworten", self.page.locator("#progress-summary").inner_text())

    def test_learning_cards_and_keyboard_without_scoring(self):
        self.choose(["beitou", "shilin"])
        self.page.locator("#language").select_option("en")
        self.page.locator('[data-mode="cards"]').click()
        self.page.locator("#start-button").click()
        self.assertIn("1 / 2", self.page.locator("#session-count").inner_text())
        self.assertIn("Dist.", self.page.locator("#question-name").inner_text())
        self.assertFalse(self.page.locator("#question-secondary").is_visible())
        self.page.locator(f'.district-shape[data-id="{self.target()["id"]}"]').press("Enter")
        self.assertTrue(self.page.locator("#next-button").is_visible())
        self.page.locator("#next-button").click()
        self.page.locator("#language").select_option("zh")
        self.assertIn("區", self.page.locator("#question-name").inner_text())
        self.page.locator("#reveal-button").click()
        self.page.locator("#next-button").click()
        self.assertIn("2 Karten", self.page.locator("#result-score").inner_text())
        self.assertIsNone(self.progress())

    def test_drag_does_not_submit_answer(self):
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        point = self.page.locator('.district-shape[data-id="shilin"]').evaluate("""el => {
            const p = new DOMPoint(Number(el.dataset.anchorX), Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        before = self.page.locator("#map-content").get_attribute("transform")
        self.page.mouse.move(point["x"], point["y"])
        self.page.mouse.down()
        self.page.mouse.move(point["x"] + 70, point["y"] + 30, steps=10)
        self.page.mouse.up()
        self.assertNotEqual(before, self.page.locator("#map-content").get_attribute("transform"))
        self.assertFalse(self.page.locator("#feedback").is_visible())
        self.assertIsNone(self.progress())
        self.page.locator("#zoom-reset").click()
        self.page.wait_for_timeout(200)
        self.click_district(self.target()["id"])
        self.assertTrue(self.page.locator("#feedback").is_visible())

    def test_empty_selection_and_bad_storage(self):
        self.choose([])
        self.assertTrue(self.page.locator("#start-button").is_disabled())
        self.assertIn("mindestens einen Bezirk", self.page.locator("#selection-note").inner_text())
        self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1', '{invalid');")
        self.page.reload()
        self.page.locator("#select-all").click()
        self.assertFalse(self.page.locator("#start-button").is_disabled())
        self.assertEqual(self.page.locator(".district-shape:not(.is-muted)").count(), 41)
        self.page.locator("#progress-open").click()
        self.assertIn("ersten Quizantworten", self.page.locator("#progress-summary").inner_text())
        self.assertFalse(self.page.evaluate("document.documentElement.scrollWidth > innerWidth"))

    def test_city_scope_focus_and_complete_new_taipei_round(self):
        self.page.locator("#city-scope").select_option("new-taipei")
        self.assertEqual(self.page.locator("#district-picker input").count(), 29)
        self.assertEqual(self.page.locator(".district-shape:not(.is-muted)").count(), 29)
        self.assertEqual(self.page.locator("#map-title").inner_text(), "New Taipei City")
        self.choose(["nt-yonghe"])
        district = self.page.locator('.district-shape[data-id="nt-yonghe"]')
        before = district.bounding_box()["width"]
        self.page.locator("#focus-selected").click()
        self.assertGreater(district.bounding_box()["width"], before * 5)
        self.click_district("nt-yonghe")
        self.assertIn("New Taipei City", self.page.locator("#map-detail").inner_text())
        self.page.locator("#city-scope").select_option("taipei")
        self.assertEqual(self.page.locator("#district-picker input").count(), 12)
        self.assertEqual(self.page.locator(".district-shape:not(.is-muted)").count(), 12)
        self.page.locator("#city-scope").select_option("new-taipei")
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#round-size").select_option("all")
        self.page.locator("#start-button").click()
        self.assertIn("1 / 29", self.page.locator("#session-count").inner_text())
        visited = set()
        for _ in range(29):
            target = self.target()
            self.assertEqual(target["cityId"], "new-taipei")
            self.assertNotIn(target["id"], visited)
            self.assertIn("New Taipei City", self.page.locator("#question-city").inner_text())
            visited.add(target["id"])
            self.click_district(target["id"])
            self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
            self.page.locator("#next-button").click()
        self.assertEqual(len(visited), 29)
        self.assertIn("29 / 29", self.page.locator("#result-score").inner_text())
        self.assertTrue(all(id.startswith("nt-") for id in self.progress()["districts"]))

    def test_mixed_city_quiz_and_city_context(self):
        self.choose(["neihu", "nt-banqiao", "nt-tamsui"])
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        visited = set()
        for _ in range(3):
            target = self.target()
            visited.add(target["id"])
            expected = "New Taipei City" if target["cityId"] == "new-taipei" else "臺北市"
            self.assertIn(expected, self.page.locator("#question-city").inner_text())
            self.click_district(target["id"])
            self.page.locator("#next-button").click()
        self.assertEqual(visited, {"neihu", "nt-banqiao", "nt-tamsui"})
        self.assertIn("3 / 3", self.page.locator("#result-score").inner_text())
        self.assertEqual(self.progress()["districts"]["neihu"]["correct"], 1)
        self.assertEqual(self.progress()["districts"]["nt-banqiao"]["correct"], 1)

    def test_legacy_progress_and_settings_migrate_without_reset(self):
        legacy_ids = [feature["id"] for feature in self.features if feature["cityId"] == "taipei"]
        progress = {"rounds": 3, "districts": {"neihu": {"attempts": 7, "correct": 5}}}
        settings = {"selected": legacy_ids, "roundSize": 12, "mode": "quiz", "language": "en", "labels": False, "metro": False}
        self.page.evaluate("payload => { localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify(payload.progress)); localStorage.setItem('taipei-kennen.settings.v1',JSON.stringify(payload.settings)); }", {"progress": progress, "settings": settings})
        self.page.reload()
        self.assertEqual(self.progress(), progress)
        self.assertEqual(self.page.locator("#city-scope").input_value(), "all")
        self.assertEqual(self.page.locator("#district-picker input:checked").count(), 41)
        self.assertEqual(self.page.locator("#round-size").input_value(), "all")
        self.assertIn("41 Aufgaben", self.page.locator("#start-button").inner_text())
        self.assertFalse(self.page.locator("#show-metro").is_checked())
        self.assertFalse(self.page.locator("#show-labels-taipei").is_checked())
        self.assertFalse(self.page.locator("#show-labels-new-taipei").is_checked())
        self.page.locator("#city-scope").select_option("new-taipei")
        self.page.reload()
        self.assertEqual(self.page.locator("#city-scope").input_value(), "new-taipei")
        self.assertEqual(self.page.locator("#district-picker input:checked").count(), 29)
        self.assertFalse(self.page.locator("#show-labels-taipei").is_checked())
        self.assertFalse(self.page.locator("#show-labels-new-taipei").is_checked())
        self.assertEqual(self.progress(), progress)
        self.page.locator("#progress-open").click()
        self.assertIn("7 beantwortete Aufgaben", self.page.locator("#progress-summary").inner_text())
        self.assertEqual(self.page.locator(".progress-city").count(), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
