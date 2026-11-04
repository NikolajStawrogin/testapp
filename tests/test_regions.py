"""Region entry, data isolation and Düsseldorf learning regressions."""
import json
import unittest
import test_browser as fixtures
from flow_helpers import GuidedFlow

class RegionBrowserTests(GuidedFlow, unittest.TestCase):
    setUpClass=classmethod(fixtures.BrowserTests.setUpClass.__func__)
    tearDownClass=classmethod(fixtures.BrowserTests.tearDownClass.__func__)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1050})
        self.context.add_init_script("try { localStorage.setItem('stadt-kennen.ui-language.v1', 'en'); } catch {}")
        self.page=self.context.new_page();self.errors=[];self.requests=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.on('request',lambda r:self.requests.append(r.url))
    def tearDown(self):
        self.assertEqual(self.errors,[])
        self.assertFalse(any(url.startswith(('http:','https:')) and not url.startswith(self.url) for url in self.requests))
        self.context.close()
    def open(self,region=None):
        self.page.goto(self.url+('' if not region else '?region='+region))
        if region:self.page.wait_for_selector('body[data-ready="true"]',state='attached')
    def chapter(self,topic):self.configure_topic(topic)
    def district_tap(self,id):
        p=self.page.locator(f'.district-shape[data-id="{id}"]').evaluate('''el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}''')
        self.page.mouse.click(p['x'],p['y'])

    def river_point(self,id):
        self.page.locator('#taipei-map').scroll_into_view_if_needed()
        return self.page.locator(f'.river-hit[data-id="{id}"]').evaluate("""el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}""")

    def test_city_entry_loads_only_selected_data_and_topics(self):
        self.open();self.assertFalse(any('/data/'in url for url in self.requests))
        self.page.locator('[data-region="duesseldorf"]').click();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertTrue(self.page.locator('#home-view').is_visible());self.assertFalse(any('/data/streets.js'in u for u in self.requests))
        self.assertTrue(any('/data/duesseldorf.js'in u for u in self.requests))
    def test_neighborhood_scope_names_and_quiz(self):
        self.open('duesseldorf');self.chapter('districts')
        labels=self.page.locator('#city-scope option').all_text_contents();self.assertEqual(len(labels),51);self.assertIn('Eller',labels);self.assertIn('Wersten',labels)
        self.assertFalse(any('Borough'in label for label in labels));self.page.locator('#city-scope').select_option('dd-eller');self.finish_setup('quiz')
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Eller');self.district_tap('dd-eller')
        self.assertIn('Exactly right',self.page.locator('#feedback').inner_text());self.page.locator('#next-button').click();self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
        self.go_step(1);self.page.locator('#city-scope').select_option('all');self.page.locator('#select-all').click()
        for id in ['dd-eller','dd-wersten']:self.page.locator(f'#district-picker input[value="{id}"]').check()
        self.finish_setup('quiz');self.assertIn(self.page.locator('#question-name').inner_text(),['Eller','Wersten'])
    def test_old_numbered_selection_migrates_and_keeps_progress(self):
        self.open('duesseldorf')
        self.page.evaluate('''()=>{localStorage.setItem('duesseldorf-kennen.settings.v1',JSON.stringify({selected:['dd-b3'],areaLevel:'borough',scope:'all',labels:false}));localStorage.setItem('duesseldorf-kennen.progress.v1',JSON.stringify({rounds:2,districts:{'dd-b3':{attempts:2,correct:1}}}))}''')
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.chapter('districts')
        self.assertGreater(self.page.locator('#district-picker input:checked').count(),1)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('duesseldorf-kennen.progress.v1')).districts['dd-b3'].correct"),1)
        self.finish_setup('explore');self.assertFalse(self.page.locator('#area-level-field').is_visible());self.assertEqual(self.page.locator('.district-label:visible').count(),0)
    def test_street_quiz_and_taipei_progress_are_separate(self):
        self.open('duesseldorf');self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify({rounds:4,districts:{daan:{attempts:3,correct:2}}}))")
        self.chapter('streets');self.go_step(2);self.page.locator('#street-learning-path').select_option('free');self.page.locator('#street-search').fill('Königsallee')
        self.page.wait_for_function("document.querySelectorAll('#street-picker input').length===1");self.finish_setup('quiz')
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Königsallee');self.page.locator('#reveal-button').click();self.page.locator('#next-button').click()
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('taipei-kennen.progress.v1')).rounds"),4)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('duesseldorf-kennen.progress.v1')).rounds"),1)
    def test_wrong_region_backup_is_rejected(self):
        self.open('duesseldorf');self.open_progress()
        import json
        payload={'app':'taipei-kennen','region':'taipei','formatVersion':1,'progress':{'rounds':0,'districts':{}}}
        self.page.locator('#import-progress').set_input_files({'name':'other.json','mimeType':'application/json','buffer':json.dumps(payload).encode()})
        self.page.wait_for_function("document.querySelector('#toast').textContent.includes('another city')")
        self.assertFalse(self.page.locator('#import-confirmation').is_visible())
    def test_transit_kinds_toggle_persist_and_do_not_answer_quiz(self):
        self.open('duesseldorf');self.chapter('districts');self.page.locator('#city-scope').select_option('dd-eller');self.go_step(3)
        self.page.locator('[data-transport-kind="suburban"]').uncheck();self.finish_setup('quiz')
        self.assertEqual(self.page.locator('.metro-line').count(),26);self.assertEqual(self.page.locator('.metro-line[data-kind="suburban"]:visible').count(),0)
        self.open_settings();self.page.locator('[data-transport-kind="metro"]').uncheck();self.close_dialog('settings')
        self.assertFalse(self.page.locator('#feedback').is_visible());self.assertIsNone(self.page.evaluate("localStorage.getItem('duesseldorf-kennen.progress.v1')"))
    def test_river_quiz_wrong_answer_retry_and_name_visibility(self):
        self.open('duesseldorf');self.chapter('rivers');self.go_step(2);self.page.locator('[data-mode="quiz"]').click();self.page.locator('#round-size').select_option('all');self.finish_setup()
        rivers=self.page.evaluate('DUESSELDORF_DATA.rivers.features.map(({id,nameZh})=>({id,nameZh}))');first=None
        for i in range(6):
            name=self.page.locator('#question-name').inner_text();target=next(r for r in rivers if r['nameZh']==name)
            self.assertFalse(self.page.locator(f'.river-label[data-id="{target["id"]}"]').is_visible())
            chosen=next(r for r in rivers if r['id']!=target['id'])if i==0 else target
            if i==0:first=target
            self.page.locator(f'.river-hit[data-id="{chosen["id"]}"]').dispatch_event('keydown',{'key':'Enter'});self.page.locator('#next-button').click()
        self.assertIn('5 / 6',self.page.locator('#result-score').inner_text());self.page.locator('#retry-errors').click()
        self.page.locator(f'.river-hit[data-id="{first["id"]}"]').dispatch_event('keydown',{'key':'Enter'});self.page.locator('#next-button').click()
        self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
