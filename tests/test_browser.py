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
from flow_helpers import GuidedFlow


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_KEY = "taipei-kennen.progress.v1"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class BrowserTests(GuidedFlow, unittest.TestCase):
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
        self.context.add_init_script("try { localStorage.setItem('stadt-kennen.ui-language.v1', 'en'); } catch {}")
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
        self.configure_topic('districts');self.finish_setup('explore')

    def choose(self, ids):
        self.go_step(1)
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


    def progress(self):
        return self.page.evaluate("key => JSON.parse(localStorage.getItem(key) || 'null')", PROGRESS_KEY)


    def test_map_exploration_zoom_labels_and_city_scope(self):
        self.assertTrue(self.page.locator('.map-panel').is_visible())
        self.assertEqual(self.page.locator('.district-shape').count(),41)
        before=self.page.locator('#map-content').get_attribute('transform')
        self.page.locator('#zoom-in').click();self.assertNotEqual(before,self.page.locator('#map-content').get_attribute('transform'))
        self.open_settings();self.page.locator('#show-labels-taipei').uncheck();self.close_dialog('settings')
        visible=self.page.locator('.district-label:visible').evaluate_all('nodes=>nodes.map(n=>TAIPEI_DATA.features.find(f=>f.id===n.dataset.id).cityId)')
        self.assertTrue(visible);self.assertEqual(set(visible),{'new-taipei'})
        self.go_step(1);self.page.locator('#city-scope').select_option('taipei');self.finish_setup('explore')
        self.assertEqual(self.page.locator('.district-shape:not(.is-muted)').count(),12)
        self.click_district('neihu');self.assertIn('內湖區',self.page.locator('#map-detail').inner_text())

    def test_quiz_scoring_repeat_persistence_and_delete(self):
        self.choose(['neihu','shilin','beitou']);self.go_step(2);self.page.locator('[data-mode="quiz"]').click();self.page.locator('#round-size').select_option('all');self.finish_setup()
        first=self.target();wrong=next(f for f in self.features if f['id']in ['neihu','shilin','beitou']and f['id']!=first['id'])
        self.click_district(wrong['id']);self.assertTrue(self.page.locator('#feedback.wrong').is_visible());self.page.locator('#next-button').click()
        self.click_district(self.target()['id']);self.page.locator('#next-button').click();self.page.locator('#reveal-button').click();self.page.locator('#next-button').click()
        self.assertIn('1 / 3',self.page.locator('#result-score').inner_text());self.assertFalse(self.page.locator('.map-panel').is_visible())
        self.page.locator('#retry-errors').click()
        for _ in range(2):self.click_district(self.target()['id']);self.page.locator('#next-button').click()
        self.assertIn('2 / 2',self.page.locator('#result-score').inner_text());self.assertEqual(self.progress()['rounds'],2)
        self.open_progress();self.assertIn('5 questions answered',self.page.locator('#progress-summary').inner_text())
        self.page.locator('#delete-progress').click();self.page.locator('#delete-confirm').click();self.assertIsNone(self.progress())
        self.close_dialog('progress');self.assertTrue(self.page.locator('#setup-view').is_visible())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.assertIsNone(self.progress())

    def test_river_only_quiz_scoring_retry_and_persistence(self):
        self.configure_topic('rivers');self.page.locator('#city-scope').select_option('new-taipei');self.go_step(2)
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#round-size').select_option('all');self.finish_setup()
        first=None
        for index in range(4):
            target=self.target();self.assertEqual(target['kind'],'river')
            self.assertFalse(self.page.locator(f'.river-label[data-id="{target["id"]}"]').is_visible())
            if index==0:
                first=target;other=next(f for f in self.rivers if f['id']!=target['id']);self.click_river(other['id'])
            else:self.click_river(target['id'])
            self.assertTrue(self.page.locator(f'.river-shape[data-id="{target["id"]}"]').evaluate('el=>el.classList.contains("is-correct")'))
            self.page.locator('#next-button').click()
        self.assertIn('3 / 4',self.page.locator('#result-score').inner_text());self.page.locator('#retry-errors').click()
        self.click_river(first['id']);self.page.locator('#next-button').click();self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
        self.assertEqual(self.progress()['districts'][first['id']],{'attempts':2,'correct':1})

    def test_mixed_river_quiz_scope_selection_and_cards(self):
        self.choose(['neihu']);self.page.locator('#include-rivers').check()
        for item in self.page.locator('#river-picker input').all():item.set_checked(item.get_attribute('value')=='river-tamsui')
        self.go_step(2);self.page.locator('[data-mode="quiz"]').click();self.page.locator('#round-size').select_option('all');self.finish_setup()
        visited=set()
        for _ in range(2):
            target=self.target();visited.add(target['id'])
            (self.click_river if target.get('kind')=='river'else self.click_district)(target['id']);self.page.locator('#next-button').click()
        self.assertEqual(visited,{'neihu','river-tamsui'});before=self.progress()
        self.configure_topic('rivers');self.finish_setup('cards');self.page.locator('#reveal-button').click();self.page.locator('#next-button').click()
        self.assertIn('1 card',self.page.locator('#result-score').inner_text());self.assertEqual(self.progress(),before)

    def test_learning_cards_and_keyboard_without_scoring(self):
        self.choose(['beitou','shilin']);self.go_step(3);self.page.locator('#language').select_option('en');self.wait_idle();self.finish_setup('cards')
        self.assertIn('Dist.',self.page.locator('#question-name').inner_text())
        for _ in range(2):
            self.page.locator(f'.district-shape[data-id="{self.target()["id"]}"]').press('Enter');self.page.locator('#next-button').click()
        self.assertIn('2 cards',self.page.locator('#result-score').inner_text());self.assertIsNone(self.progress())

    def test_legacy_progress_and_settings_migrate_without_reset(self):
        payload={'rounds':3,'districts':{'neihu':{'attempts':4,'correct':3}}}
        self.page.evaluate('(p)=>{localStorage.setItem("taipei-kennen.progress.v1",JSON.stringify(p));localStorage.setItem("taipei-kennen.settings.v1",JSON.stringify({language:"en",labels:false,selected:["neihu"],scope:"taipei"}))}',payload)
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertTrue(self.page.locator('#home-view').is_visible());self.configure_topic('districts');self.finish_setup('quiz')
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Neihu Dist.');self.assertEqual(self.progress(),payload)
        self.assertEqual(self.page.locator('.district-label:visible').count(),0)

    def test_touch_pinch_pan_and_tap_do_not_confuse_quiz_answers(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("localStorage.setItem('stadt-kennen.ui-language.v1','en')")
        self.page=self.context.new_page();self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.goto(self.url+'?region=taipei');self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.configure_topic('districts');self.choose(['neihu']);self.finish_setup('quiz')
        svg=self.page.locator('#taipei-map');svg.scroll_into_view_if_needed();box=svg.bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
        cdp=self.context.new_cdp_session(self.page)
        def touch(kind,points):cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':[{'id':i,'x':px,'y':py,'radiusX':2,'radiusY':2,'force':1}for i,px,py in points]})
        before=self.page.locator('#map-content').get_attribute('transform')
        touch('touchStart',[(1,x-35,y),(2,x+35,y)]);touch('touchMove',[(1,x-65,y),(2,x+65,y)]);touch('touchEnd',[])
        self.assertNotEqual(before,self.page.locator('#map-content').get_attribute('transform'));self.assertFalse(self.page.locator('#feedback').is_visible())
        self.page.locator('#zoom-reset').click();self.page.wait_for_timeout(350)
        point=self.page.locator('.district-shape[data-id="neihu"]').evaluate('el=>{const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return{x:p.x,y:p.y}}')
        self.page.touchscreen.tap(point['x'],point['y']);self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))

    def test_empty_selection_and_bad_storage(self):
        self.choose([]);self.assertTrue(self.page.locator('#wizard-next').is_disabled());self.assertTrue(self.page.locator('#wizard-validation').is_visible())
        self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1','{invalid')")
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.open_progress();self.assertIn('first quiz answers',self.page.locator('#progress-summary').inner_text())


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


    def test_drag_does_not_submit_answer(self):
        self.finish_setup('quiz')
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


    def test_metro_track_is_geographically_aligned_and_clicks_reach_district(self):
        self.choose(["nangang"])
        self.finish_setup('quiz')
        self.page.locator("#taipei-map").scroll_into_view_if_needed()
        point = self.page.locator('.metro-line[data-line="BR"]').evaluate("""el => {
            const p = el.getPointAtLength(0).matrixTransform(el.getScreenCTM());
            return {x:p.x,y:p.y};
        }""")
        hit = self.page.evaluate("p => document.elementFromPoint(p.x,p.y)?.closest('.district-shape')?.dataset.id", point)
        self.assertEqual(hit, "nangang", "The Wenhu terminus must align with the Nangang district and allow clicks through the line")
        self.assertIsNone(self.progress())
        self.page.mouse.click(point["x"], point["y"])
        self.assertIn('Exactly right', self.page.locator("#feedback").inner_text())
        self.assertEqual(self.progress()["districts"]["nangang"]["attempts"], 1)


    def test_river_confluence_prefers_water_over_neighbour_hit_padding(self):
        self.go_step(1);self.page.locator('#include-rivers').check();self.finish_setup('explore')
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

    def test_city_labels_are_independent_of_quiz_scope(self):
        self.go_step(1);self.page.locator('#city-scope').select_option('taipei');self.go_step(3)
        self.page.locator('#show-labels-taipei').uncheck();self.finish_setup('quiz')
        def visible():return self.page.locator('.district-label:visible').evaluate_all('nodes=>nodes.map(n=>TAIPEI_DATA.features.find(f=>f.id===n.dataset.id).cityId)')
        self.assertTrue(visible());self.assertEqual(set(visible()),{'new-taipei'})
        target=self.target();self.assertFalse(self.page.locator(f'.district-label[data-id="{target["id"]}"]').is_visible())
        self.click_district('nt-sanchong');self.assertIsNone(self.progress())
        transform=self.page.locator('#map-content').get_attribute('transform');self.open_settings()
        self.page.locator('#show-labels-new-taipei').uncheck();self.close_dialog('settings');self.assertEqual(visible(),[])
        self.open_settings();self.page.locator('#show-labels-new-taipei').check();self.close_dialog('settings')
        self.assertEqual(set(visible()),{'new-taipei'});self.assertEqual(transform,self.page.locator('#map-content').get_attribute('transform'))

    def test_metro_layer_toggle_persistence_and_language(self):
        self.assertEqual(self.page.locator('.metro-line').count(),13);self.assertEqual(self.page.locator('.metro-chip').count(),12)
        self.open_settings();self.page.locator('#show-metro').uncheck();self.close_dialog('settings');self.assertFalse(self.page.locator('#metro-layer').is_visible())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.configure_topic('districts');self.go_step(3)
        self.assertFalse(self.page.locator('#show-metro').is_checked());self.page.locator('#show-metro').check();self.page.locator('#language').select_option('en');self.wait_idle();self.finish_setup('explore')
        self.page.locator('#metro-legend summary').click();self.assertEqual(self.page.locator('.metro-chip[data-line="BR"] .metro-name').inner_text(),'Wenhu')
