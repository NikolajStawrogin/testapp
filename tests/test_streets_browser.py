"""Street learning, navigation, backup and mobile interaction regressions."""

import json
import unittest

import test_browser as fixtures


class StreetBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.BrowserTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.BrowserTests.tearDownClass.__func__(cls)

    setUp = fixtures.BrowserTests.setUp
    tearDown = fixtures.BrowserTests.tearDown
    open_practice = fixtures.BrowserTests.open_practice
    choose = fixtures.BrowserTests.choose
    progress = fixtures.BrowserTests.progress

    def street_mode(self, scope="taipei"):
        self.page.locator('[data-subject="streets"]').click()
        self.page.locator("#city-scope").select_option(scope)

    def search(self, text):
        self.page.locator("#street-search").fill(text)
        self.page.wait_for_timeout(180)

    def target(self):
        return self.page.evaluate("""() => {
            const text=document.getElementById('question-name').textContent;
            return window.TAIPEI_STREETS.features.find(f => f.cityId==='taipei' && (f.nameZh===text || f.nameEn===text));
        }""")

    def point(self, id):
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        return self.page.locator(f'.street-shape[data-id="{id}"]').evaluate("""el => {
            const p=new DOMPoint(Number(el.dataset.anchorX),Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")

    def click_street(self, id):
        self.page.locator("#zoom-reset").click()
        point = self.point(id)
        self.page.mouse.move(point["x"], point["y"])
        self.page.mouse.click(point["x"], point["y"])

    def test_home_navigation_settings_and_help(self):
        self.page.evaluate("localStorage.clear()")
        self.page.reload()
        self.assertTrue(self.page.locator("#home-view").is_visible())
        self.assertEqual(self.page.locator(".home-card").count(), 3)
        self.page.locator('[data-nav="settings"]').click()
        self.assertTrue(self.page.locator("#settings-dialog").is_visible())
        self.page.locator("#show-labels-taipei").uncheck()
        self.page.locator("#show-street-labels").uncheck()
        self.page.locator("#language").select_option("zh")
        self.page.locator('[aria-label="Einstellungen schließen"]').click()
        self.page.locator('[data-nav="help"]').click()
        self.assertIn("Lanes", self.page.locator("#help-dialog").inner_text())
        self.page.locator("#help-sources").click()
        self.assertTrue(self.page.locator("#sources-dialog").is_visible())
        self.assertIn("2021", self.page.locator("#sources-dialog").inner_text())
        self.page.locator('[aria-label="Quellen schließen"]').click()
        self.page.locator('[data-start="streets"]').click()
        self.page.locator("#chapter-loading").wait_for(state="hidden")
        self.assertTrue(self.page.locator("#street-selection").is_visible())
        self.assertFalse(self.page.locator("#show-street-labels").is_checked())
        self.assertEqual(self.page.locator("#language").input_value(), "zh")
        self.page.locator('[data-nav="quiz"]').click()
        self.page.locator("#chapter-loading").wait_for(state="hidden")
        self.assertTrue(self.page.locator("#round-size-field").is_visible())
        self.page.reload()
        self.assertTrue(self.page.locator("#practice-view").is_visible())
        self.assertTrue(self.page.locator("#street-selection").is_visible())
        self.assertFalse(self.page.locator("#show-labels-taipei").is_checked())

    def test_street_quiz_hover_hidden_solution_scoring_retry_and_persistence(self):
        self.street_mode()
        self.page.locator('[name="street-unit"][value="street"]').uncheck()
        self.search("忠孝東路")
        candidates = self.page.locator("#street-picker input:checked").evaluate_all("nodes => nodes.map(node=>node.value)")
        self.assertGreater(len(candidates), 2)
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#round-size").select_option("5")
        self.page.locator("#start-button").click()
        first_error = None
        seen = set()
        for index in range(5):
            target = self.target()
            self.assertNotIn(target["id"], seen)
            seen.add(target["id"])
            self.assertFalse(self.page.locator(f'.street-label[data-id="{target["id"]}"]').is_visible())
            self.assertNotIn(target["nameZh"], self.page.locator(f'.street-shape[data-id="{target["id"]}"]').get_attribute("aria-label"))
            point = self.point(target["id"])
            self.page.mouse.move(point["x"], point["y"])
            self.assertEqual(self.page.locator(".street-highlight").get_attribute("data-id"), target["id"])
            self.assertFalse(self.page.locator("#feedback").is_visible())
            if index == 0:
                first_error = target["id"]
                chosen = next(id for id in candidates if id != first_error)
            else:
                chosen = target["id"]
            self.click_street(chosen)
            self.assertTrue(self.page.locator(f'.street-shape[data-id="{target["id"]}"]').evaluate("el => el.classList.contains('is-correct')"))
            self.assertIn("Genau richtig" if index else "Noch nicht ganz", self.page.locator("#feedback").inner_text())
            self.page.locator("#next-button").click()
        self.assertIn("4 / 5", self.page.locator("#result-score").inner_text())
        self.page.locator("#retry-errors").click()
        self.assertEqual(self.target()["id"], first_error)
        self.click_street(first_error)
        self.page.locator("#next-button").click()
        self.assertEqual(self.progress()["districts"][first_error], {"attempts": 2, "correct": 1})
        self.page.reload()
        self.assertEqual(self.progress()["rounds"], 2)
        self.page.locator("#progress-open").click()
        self.assertIn("Geübte Straßen", self.page.locator("#progress-list").inner_text())

    def test_whole_road_quiz_hides_section_and_lane_name_hints(self):
        self.street_mode()
        self.page.locator('[name="street-unit"][value="section"]').uncheck()
        self.search("忠孝東路")
        self.assertEqual(self.page.locator("#street-picker input").count(), 1)
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        target = self.target()
        self.assertEqual(target["nameZh"], "忠孝東路")
        self.assertEqual(target["unit"], "street")
        self.assertEqual(len(target["children"]), 7)
        point = self.point(target["id"])
        self.page.mouse.move(point["x"], point["y"])
        for _ in range(2):
            self.page.mouse.wheel(0, -240)
            self.page.wait_for_timeout(80)
        self.page.wait_for_function("!document.getElementById('taipei-map').classList.contains('is-moving')")
        visible_names = self.page.locator(".street-label:visible").all_text_contents()
        self.assertTrue(visible_names, "Other names should remain available as orientation")
        self.assertFalse(any("忠孝東路" in text for text in visible_names), "Section and child-lane labels must not reveal the whole road")
        self.assertEqual(self.page.locator(".street-highlight").get_attribute("data-id"), target["id"])
        self.page.mouse.click(point["x"], point["y"])
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"][target["id"]], {"attempts": 1, "correct": 1})
        self.page.reload()
        self.assertEqual(self.progress()["districts"][target["id"]]["attempts"], 1)

    def test_sections_lanes_and_alleys_have_independent_filters(self):
        self.street_mode()
        self.choose(["neihu"])
        self.page.locator('[name="street-category"][value="local"]').check()
        self.page.locator('[name="street-unit"][value="lane"]').check()
        self.page.locator('[name="street-unit"][value="alley"]').check()
        self.search("康寧路三段")

        def units():
            return set(self.page.locator("#street-picker input").evaluate_all("nodes => nodes.map(n => window.TAIPEI_STREETS.features.find(f=>f.id===n.value).unit)"))

        self.assertIn("section", units())
        self.assertIn("lane", units())
        self.assertIn("alley", units())
        self.page.locator('[name="street-unit"][value="street"]').uncheck()
        self.page.locator('[name="street-unit"][value="lane"]').uncheck()
        self.page.locator('[name="street-unit"][value="alley"]').uncheck()
        self.assertEqual(units(), {"section"})
        self.page.locator('[name="street-unit"][value="section"]').uncheck()
        self.page.locator('[name="street-unit"][value="lane"]').check()
        self.assertEqual(units(), {"lane"})
        self.page.locator('[name="street-unit"][value="lane"]').uncheck()
        self.page.locator('[name="street-unit"][value="alley"]').check()
        self.assertEqual(units(), {"alley"})
        self.page.reload()
        self.assertEqual(units(), {"alley"})
        self.assertEqual(self.page.locator("#street-search").input_value(), "康寧路三段")

    def test_outer_new_taipei_coverage_missing_names_and_empty_state(self):
        self.street_mode("new-taipei")
        self.choose(["nt-wulai"])
        self.page.locator('[name="street-category"][value="local"]').check()
        self.page.locator('[name="street-unit"][value="lane"]').check()
        self.page.locator('[name="street-unit"][value="alley"]').check()
        self.assertGreater(self.page.locator("#street-picker input").count(), 0)
        self.page.locator("#only-bilingual").uncheck()
        missing = self.page.evaluate("window.TAIPEI_STREETS.features.find(f=>f.districtIds.includes('nt-wulai')&&!f.nameEn)")
        self.assertIsNotNone(missing)
        self.search(missing["nameZh"])
        self.assertTrue(self.page.locator(f'#street-picker input[value="{missing["id"]}"]').is_visible())
        self.assertIn("Englischer Name nicht belegt", self.page.locator("#street-picker").inner_text())
        self.page.locator("#language").select_option("en")
        self.assertEqual(self.page.locator(f'#street-picker input[value="{missing["id"]}"]').count(), 0)
        self.assertTrue(self.page.locator("#only-bilingual").is_disabled())
        for item in self.page.locator('[name="street-unit"]').all():
            item.uncheck()
        self.assertTrue(self.page.locator("#street-empty").is_visible())
        self.assertTrue(self.page.locator("#start-button").is_disabled())
        self.page.reload()
        self.assertEqual(self.page.locator("#city-scope").input_value(), "new-taipei")
        self.assertTrue(self.page.locator("#street-empty").is_visible())

    def test_street_learning_cards_and_keyboard_do_not_score(self):
        self.street_mode()
        self.search("忠孝東路四段")
        self.page.locator('[data-mode="cards"]').click()
        self.page.locator("#start-button").click()
        target = self.target()
        self.assertEqual(target["nameZh"], "忠孝東路四段")
        self.page.locator("#reveal-button").click()
        self.assertIn("忠孝東路四段", self.page.locator("#feedback").inner_text())
        self.assertIsNone(self.progress())
        self.page.locator("#next-button").click()
        self.page.locator("#back-to-setup").click()
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        self.page.locator(f'.street-shape[data-id="{target["id"]}"]').focus()
        self.page.keyboard.press("Enter")
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"][target["id"]]["attempts"], 1)

    def test_menu_during_quiz_keeps_question_and_settings_do_not_submit(self):
        self.street_mode()
        self.search("忠孝東路四段")
        self.page.locator('[data-mode="quiz"]').click()
        self.page.locator("#start-button").click()
        target = self.target()
        self.page.locator('[data-nav="settings"]').click()
        self.page.locator("#show-street-labels").uncheck()
        self.page.locator("#language").select_option("en")
        self.page.locator('[aria-label="Einstellungen schließen"]').click()
        self.assertEqual(self.target()["id"], target["id"])
        self.assertIsNone(self.progress())
        self.assertFalse(self.page.locator("#feedback").is_visible())
        self.page.locator('[data-nav="home"]').click()
        self.assertTrue(self.page.locator("#home-view").is_visible())
        self.page.locator('[data-nav="continue"]').click()
        self.assertEqual(self.target()["id"], target["id"])
        self.assertTrue(self.page.locator("#session-panel").is_visible())
        self.assertIsNone(self.progress())

    def test_progress_export_import_validation_and_confirmation(self):
        original = {"rounds": 1, "districts": {"neihu": {"attempts": 2, "correct": 1}}}
        self.page.evaluate("p=>localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify(p))", original)
        self.page.reload()
        self.page.locator("#progress-open").click()
        with self.page.expect_download() as download_info:
            self.page.locator("#export-progress").click()
        download = download_info.value
        with open(download.path()) as file:
            payload = json.load(file)
        self.assertEqual(payload["progress"], original)
        self.assertEqual(payload["app"], "taipei-kennen")
        self.page.locator("#import-progress").set_input_files({"name": "invalid.json", "mimeType": "application/json", "buffer": b'{"no":"backup"}'})
        self.page.wait_for_function("document.getElementById('toast').textContent.includes('gültige')")
        self.assertIn("gültige", self.page.locator("#toast").inner_text())
        self.assertEqual(self.progress(), original)
        replacement = {"app": "taipei-kennen", "formatVersion": 1, "progress": {"rounds": 3, "districts": {"daan": {"attempts": 4, "correct": 3}}}}
        self.page.locator("#import-progress").set_input_files({"name": "backup.json", "mimeType": "application/json", "buffer": json.dumps(replacement).encode()})
        self.page.locator("#import-confirmation").wait_for(state="visible")
        self.assertEqual(self.progress(), original)
        self.page.locator("#confirm-import").click()
        self.assertEqual(self.progress(), replacement["progress"])
        self.assertIn("4 beantwortete Aufgaben", self.page.locator("#progress-summary").inner_text())

    def mobile_context(self):
        self.context.close()
        self.context = self.browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        self.page = self.context.new_page()
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.external_requests.append(request.url)
                     if request.url.startswith(("https://", "http://")) and not request.url.startswith(self.url) else None)
        self.page.goto(self.url)
        self.open_practice()

    def test_mobile_street_quiz_touch_preview_zoom_pan_and_confirmation(self):
        self.mobile_context()
        self.street_mode()
        self.choose(["daan"])
        self.page.locator('[name="street-category"][value="local"]').check()
        self.page.locator('[name="street-unit"][value="street"]').uncheck()
        self.page.locator('[name="street-unit"][value="section"]').uncheck()
        self.page.locator('[name="street-unit"][value="lane"]').check()
        lane = self.page.evaluate("window.TAIPEI_STREETS.features.find(f=>f.cityId==='taipei'&&f.districtIds.length===1&&f.districtIds.includes('daan')&&f.unit==='lane'&&f.nameEn&&f.geometry.coordinates.some(p=>p.length>3))")
        self.assertIsNotNone(lane)
        self.search(lane["nameZh"])
        self.page.locator('[data-mode="quiz"]').tap()
        self.page.locator("#start-button").tap()
        self.assertTrue(self.page.locator("#mobile-question").is_visible())
        self.assertEqual(self.page.locator("#mobile-question-name").inner_text(), lane["nameZh"])
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        client = self.context.new_cdp_session(self.page)

        def touches(kind, points):
            client.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"id": id, "x": x, "y": y} for id,x,y in points]})
            self.page.wait_for_timeout(60)

        box = self.page.locator("#taipei-map").bounding_box()
        cx, cy = box["x"] + box["width"]/2, box["y"] + box["height"]/2
        touches("touchStart", [(1,cx-35,cy),(2,cx+35,cy)])
        touches("touchMove", [(1,cx-60,cy),(2,cx+60,cy)])
        touches("touchEnd", [])
        touches("touchStart", [(1,cx,cy)])
        touches("touchMove", [(1,cx+25,cy+20)])
        touches("touchEnd", [])
        self.assertIsNone(self.progress())
        self.assertFalse(self.page.locator("#street-confirmation").is_visible())
        self.page.locator("#zoom-reset").tap()
        point = self.point(lane["id"])
        touches("touchStart", [(1,point["x"],point["y"])])
        touches("touchEnd", [])
        self.assertIsNone(self.progress(), "Touch must preview a street before submitting it")
        self.assertTrue(self.page.locator("#street-confirmation").is_visible())
        self.assertEqual(self.page.locator(".street-highlight").get_attribute("data-id"), lane["id"])
        self.page.locator("#street-confirm").tap()
        self.assertIn("Genau richtig", self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"][lane["id"]], {"attempts": 1, "correct": 1})
        self.assertFalse(self.page.evaluate("document.documentElement.scrollWidth>innerWidth"))
        self.page.locator("#mobile-next").tap()
        self.assertTrue(self.page.locator("#results-panel").is_visible())
        self.assertFalse(self.page.locator("#mobile-question").is_visible())
        self.page.locator("#menu-toggle").tap()
        self.assertGreater(float(self.page.locator("#menu-toggle").evaluate("el=>getComputedStyle(el).fontSize").replace("px", "")), 0)
        self.page.locator('[data-nav="help"]').tap()
        self.assertTrue(self.page.locator("#help-dialog").is_visible())
        self.assertEqual(self.page.locator("#menu-toggle").get_attribute("aria-expanded"), "false")

    def test_mobile_crossing_can_cycle_between_nearby_streets(self):
        self.mobile_context()
        self.street_mode()
        self.choose(["daan"])
        self.page.locator("#street-select-all").click()
        selected = []
        for name in ["忠孝東路四段", "敦化南路一段"]:
            self.search(name)
            item = self.page.locator("#street-picker input").first
            selected.append(item.get_attribute("value"))
            item.check()
        self.search("")
        self.assertEqual(self.page.locator("#street-picker input:checked").count(), 2)
        self.page.locator('[data-mode="quiz"]').tap()
        self.page.locator("#start-button").tap()
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        point = self.page.evaluate("""ids => {
            const streets=ids.map(id=>window.TAIPEI_STREETS.features.find(f=>f.id===id));
            let crossing=null;
            for(const first of streets[0].geometry.coordinates) for(let i=1;i<first.length;i++)
            for(const second of streets[1].geometry.coordinates) for(let j=1;j<second.length;j++) {
                const a=first[i-1],b=first[i],c=second[j-1],d=second[j];
                const rx=b[0]-a[0],ry=b[1]-a[1],sx=d[0]-c[0],sy=d[1]-c[1],det=rx*sy-ry*sx;
                if(Math.abs(det)<1e-15)continue;
                const t=((c[0]-a[0])*sy-(c[1]-a[1])*sx)/det,u=((c[0]-a[0])*ry-(c[1]-a[1])*rx)/det;
                if(t>=0&&t<=1&&u>=0&&u<=1)crossing=[a[0]+t*rx,a[1]+t*ry];
            }
            if(!crossing)return null;
            const refs=['neihu','wenshan'].map(id=>{
                const f=window.TAIPEI_DATA.features.find(f=>f.id===id),el=document.querySelector(`.district-shape[data-id="${id}"]`);
                return {anchor:f.anchor,pixel:new DOMPoint(Number(el.dataset.anchorX),Number(el.dataset.anchorY)).matrixTransform(el.getScreenCTM())};
            });
            const [a,b]=refs,latitude=lat=>Math.log(Math.tan(Math.PI/4+lat*Math.PI/360));
            return {x:a.pixel.x+(crossing[0]-a.anchor[0])/(b.anchor[0]-a.anchor[0])*(b.pixel.x-a.pixel.x),
                    y:a.pixel.y+(latitude(crossing[1])-latitude(a.anchor[1]))/(latitude(b.anchor[1])-latitude(a.anchor[1]))*(b.pixel.y-a.pixel.y)};
        }""", selected)
        self.assertIsNotNone(point, "The selected real streets must cross")
        client = self.context.new_cdp_session(self.page)
        client.send("Input.dispatchTouchEvent", {"type":"touchStart","touchPoints":[{"id":1,"x":point["x"],"y":point["y"]}]})
        client.send("Input.dispatchTouchEvent", {"type":"touchEnd","touchPoints":[]})
        self.page.locator("#street-confirmation").wait_for(state="visible")
        first = self.page.locator(".street-highlight").get_attribute("data-id")
        self.assertIn(first, selected)
        self.assertTrue(self.page.locator("#street-alternative").is_visible())
        self.page.locator("#street-alternative").tap()
        chosen = self.page.locator(".street-highlight").get_attribute("data-id")
        self.assertIn(chosen, selected)
        self.assertNotEqual(first, chosen)
        self.assertIsNone(self.progress())
        target = self.target()
        self.page.locator("#street-confirm").tap()
        self.assertEqual(self.progress()["districts"][target["id"]]["correct"], int(chosen == target["id"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
