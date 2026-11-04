"""Street learning, navigation, backup and mobile interaction regressions."""

import json
import unittest

import test_browser as fixtures
from flow_helpers import GuidedFlow


class StreetBrowserTests(GuidedFlow, unittest.TestCase):
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
        self.configure_topic('streets');self.page.locator('#city-scope').select_option(scope);self.go_step(2)
        self.page.locator('#street-learning-path').select_option('free')

    def search(self, text):
        self.page.locator("#wizard-street-details").evaluate("el=>el.open=true")
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














    def test_whole_road_quiz_hides_section_and_lane_name_hints(self):
        self.street_mode();self.page.locator('[name="street-unit"][value="section"]').uncheck();self.search('忠孝東路');self.finish_setup('quiz')
        target=self.target();self.assertEqual(target['unit'],'street');self.assertEqual(target['nameZh'],'忠孝東路')
        labels=self.page.locator('.street-label:visible').all_text_contents();self.assertFalse(any('忠孝東路'in text for text in labels))
        self.page.locator(f'.street-shape[data-id="{target["id"]}"]').press('Enter');self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())
        self.assertTrue(self.page.locator('.street-solution').get_attribute('d'));self.page.locator('#next-button').click()
        self.assertIn('1 / 1',self.page.locator('#result-score').inner_text());self.assertEqual(self.progress()['districts'][target['id']],{'attempts':1,'correct':1})

    def test_sections_lanes_and_alleys_have_independent_filters(self):
        self.street_mode()
        for item in self.page.locator('[name="street-category"]').all():item.check()
        for unit in ['section','lane','alley']:
            for item in self.page.locator('[name="street-unit"]').all():item.set_checked(item.get_attribute('value')==unit)
            ids=self.page.locator('#street-picker input').evaluate_all('nodes=>nodes.map(n=>n.value)');self.assertTrue(ids)
            self.assertTrue(self.page.evaluate('(ids)=>ids.every(id=>TAIPEI_STREETS.features.find(f=>f.id===id).unit===document.querySelector("[name=street-unit]:checked").value)',ids))
        for item in self.page.locator('[name="street-unit"]').all():item.set_checked(item.get_attribute('value')=='street')
        self.search('忠孝東路');self.assertIn('忠孝東路',self.page.locator('#street-picker').inner_text())

    def test_outer_new_taipei_coverage_missing_names_and_empty_state(self):
        self.street_mode('new-taipei');self.page.locator('#only-bilingual').uncheck()
        missing=self.page.evaluate('TAIPEI_STREETS.features.find(f=>f.cityId==="new-taipei"&&!f.nameEn&&f.unit==="street"&&["major","secondary"].includes(f.category))')
        self.assertTrue(missing);self.search(missing['nameZh']);self.assertIn('English name not verified',self.page.locator('#street-picker').inner_text())
        self.go_step(3);self.page.locator('#language').select_option('en');self.wait_idle();self.go_step(2)
        self.assertEqual(self.page.locator('#street-picker input').count(),0);self.assertTrue(self.page.locator('#wizard-next').is_disabled())
        self.open_settings();self.page.locator('#language').select_option('zh');self.wait_idle();self.close_dialog('settings')
        self.assertGreater(self.page.locator('#street-picker input').count(),0)

    def test_street_learning_cards_and_keyboard_do_not_score(self):
        self.street_mode();self.search('忠孝東路四段');self.finish_setup('cards')
        target=self.target();self.page.locator(f'.street-shape[data-id="{target["id"]}"]').press('Enter')
        self.assertIn(target['nameZh'],self.page.locator('#feedback').inner_text());self.page.locator('#next-button').click()
        self.assertIsNone(self.progress());self.assertTrue(self.page.locator('#results-panel').is_visible())

    def test_menu_during_quiz_keeps_question_and_settings_do_not_submit(self):
        self.street_mode();self.search('忠孝東路四段');self.finish_setup('quiz');target=self.target()
        self.open_settings();self.page.locator('#show-street-labels').uncheck();self.page.locator('#language').select_option('en');self.wait_idle();self.close_dialog('settings')
        self.assertEqual(self.target()['id'],target['id']);self.assertIsNone(self.progress());self.assertFalse(self.page.locator('#feedback').is_visible())
        self.page.locator(f'.street-shape[data-id="{target["id"]}"]').press('Enter');self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())

    def test_progress_export_import_validation_and_confirmation(self):
        self.street_mode();self.search('忠孝東路四段');self.finish_setup('quiz');target=self.target()
        self.page.locator(f'.street-shape[data-id="{target["id"]}"]').press('Enter');self.page.locator('#next-button').click();original=self.progress()
        self.open_progress()
        with self.page.expect_download()as download:self.page.locator('#export-progress').click()
        from pathlib import Path
        payload=json.loads(Path(download.value.path()).read_text());self.assertEqual(payload['progress'],original)
        self.page.locator('#import-progress').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{}'})
        self.page.wait_for_function('document.querySelector("#toast").textContent.includes("valid")');self.assertEqual(self.progress(),original)
        payload['progress']={'rounds':3,'districts':{target['id']:{'attempts':4,'correct':3}}}
        self.page.locator('#import-progress').set_input_files({'name':'progress.json','mimeType':'application/json','buffer':json.dumps(payload).encode()})
        self.page.locator('#import-confirmation').wait_for(state='visible');self.assertEqual(self.progress(),original)
        self.page.locator('#confirm-import').click();self.assertEqual(self.progress(),payload['progress'])

    def test_mobile_street_quiz_touch_preview_zoom_pan_and_confirmation(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("localStorage.setItem('stadt-kennen.ui-language.v1','en')")
        self.page=self.context.new_page();self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.goto(self.url+'?region=taipei');self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.configure_topic('streets');self.page.locator('#city-scope').select_option('taipei');self.go_step(2)
        self.page.locator('#street-learning-path').select_option('free');self.page.locator('[name="street-unit"][value="section"]').uncheck();self.search('忠孝東路');self.finish_setup('quiz')
        target=self.target();point=self.point(target['id']);self.page.touchscreen.tap(point['x'],point['y'])
        self.assertTrue(self.page.locator('#street-confirmation').is_visible());self.assertIsNone(self.progress())
        self.page.locator('#street-confirm').tap();self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())
        self.assertEqual(self.progress()['districts'][target['id']]['correct'],1)
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))

    def test_home_navigation_settings_and_help(self):
        self.open_menu();self.page.locator('[data-nav="home"]').click();self.assertTrue(self.page.locator('#home-view').is_visible())
        self.open_menu();self.page.locator('[data-nav="help"]').click();self.assertIn('lanes',self.page.locator('#help-dialog').inner_text())
        self.page.locator('#help-sources').click();self.assertIn('2021',self.page.locator('#sources-dialog').inner_text());self.close_dialog('sources')
        self.configure_topic('streets');self.go_step(3);self.page.locator('#show-labels-taipei').uncheck();self.page.locator('#language').select_option('zh');self.wait_idle();self.finish_setup('explore')
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.configure_topic('streets');self.go_step(3)
        self.assertFalse(self.page.locator('#show-labels-taipei').is_checked());self.assertEqual(self.page.locator('#language').input_value(),'zh')


    def test_mobile_crossing_can_cycle_between_nearby_streets(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("localStorage.setItem('stadt-kennen.ui-language.v1','en')")
        self.page=self.context.new_page();self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.goto(self.url+'?region=taipei');self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.street_mode()
        self.choose(["daan"]);self.go_step(2)
        self.page.locator("#street-select-all").click()
        selected = []
        for name in ["忠孝東路四段", "敦化南路一段"]:
            self.search(name)
            item = self.page.locator("#street-picker input").first
            selected.append(item.get_attribute("value"))
            item.check()
        self.search("")
        self.assertEqual(self.page.locator("#street-picker input:checked").count(), 2)
        self.finish_setup('quiz')
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
