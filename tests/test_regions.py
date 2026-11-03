"""Region entry, data isolation and Düsseldorf learning regressions."""
import json
import unittest
import test_browser as fixtures

class RegionBrowserTests(unittest.TestCase):
    setUpClass=classmethod(fixtures.BrowserTests.setUpClass.__func__)
    tearDownClass=classmethod(fixtures.BrowserTests.tearDownClass.__func__)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1050})
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
    def chapter(self,topic):
        self.page.locator(f'[data-start="{topic}"]').click()
        self.page.locator('#chapter-loading').wait_for(state='hidden')
    def district_tap(self,id):
        p=self.page.locator(f'.district-shape[data-id="{id}"]').evaluate('''el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}''')
        self.page.mouse.click(p['x'],p['y'])
    def test_city_entry_loads_only_selected_data_and_topics(self):
        self.open();self.assertTrue(self.page.locator('#region-view').is_visible())
        self.assertFalse(any('/data/' in url for url in self.requests))
        self.page.locator('[data-region="duesseldorf"]').click()
        self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertTrue(self.page.locator('#home-view').is_visible())
        self.assertIn('Düsseldorf',self.page.locator('#page-heading').inner_text())
        self.assertFalse(any('/data/streets.js' in url for url in self.requests))
        self.assertTrue(any('/data/duesseldorf.js' in url for url in self.requests))
        self.page.screenshot(path='/workspace/duesseldorf-home.png',full_page=True)
    def test_both_area_levels_scope_labels_and_correct_quiz(self):
        self.open('duesseldorf');self.chapter('districts')
        self.assertEqual(self.page.locator('#district-picker input').count(),50)
        self.assertEqual(self.page.locator('.district-shape:visible').count(),50)
        self.page.locator('#city-scope').select_option('dd-b3')
        self.assertEqual(self.page.locator('#district-picker input').count(),8)
        self.district_tap('dd-bilk')
        self.assertIn('Bilk',self.page.locator('#map-detail').inner_text())
        self.page.locator('#area-level').select_option('borough')
        self.assertEqual(self.page.locator('#district-picker input').count(),1)
        self.assertEqual(self.page.locator('.district-shape:visible').count(),10)
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#start-button').click()
        self.assertIn('Stadtbezirk 3',self.page.locator('#question-name').inner_text())
        self.district_tap('dd-bezirk-3');self.assertIn('Genau richtig',self.page.locator('#feedback').inner_text())
        self.assertIn('Lösung: Stadtbezirk 3',self.page.locator('#map-detail').inner_text())
        self.page.locator('#next-button').click()
        self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertEqual(self.page.locator('#area-level').input_value(),'borough')
        self.assertEqual(self.page.locator('#language').input_value(),'de')
    def test_street_quiz_and_taipei_progress_are_separate(self):
        self.open('duesseldorf')
        self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify({rounds:4,districts:{daan:{attempts:3,correct:2}}}))")
        self.chapter('streets');self.page.locator('#street-search').fill('Königsallee')
        self.page.wait_for_function("document.querySelectorAll('#street-picker input').length===1")
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#start-button').click()
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Königsallee')
        self.page.locator('#reveal-button').click();self.assertTrue(self.page.locator('.street-solution').get_attribute('d'))
        self.assertIn('Königsallee',self.page.locator('#map-detail').inner_text())
        self.page.locator('#next-button').click()
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('duesseldorf-kennen.progress.v1')).rounds"),1)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('taipei-kennen.progress.v1')).rounds"),4)
        self.page.screenshot(path='/workspace/duesseldorf-streets.png',full_page=True)
        self.open('taipei');self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('taipei-kennen.progress.v1')).districts.daan.correct"),2)
        self.page.locator('.region-change').click();self.page.locator('[data-region="duesseldorf"]').click()
        self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertTrue(self.page.locator('#home-view').is_visible(),'Choosing a city always opens themes')
    def test_wrong_region_backup_is_rejected(self):
        self.open('duesseldorf');self.page.locator('[data-nav="progress"]').click()
        payload={'app':'taipei-kennen','formatVersion':1,'progress':{'rounds':5,'districts':{'daan':{'attempts':1,'correct':1}}}}
        self.page.locator('#import-progress').set_input_files({'name':'taipei.json','mimeType':'application/json','buffer':json.dumps(payload).encode()})
        self.assertIn('anderen Stadt',self.page.locator('#toast').inner_text())
        self.assertFalse(self.page.locator('#import-confirmation').is_visible())
    def test_mobile_german_layout_touch_selection_and_pending_data_status(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.page=self.context.new_page();self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.on('request',lambda r:self.requests.append(r.url))
        self.open('duesseldorf');complete=self.page.evaluate('window.DUESSELDORF_DATA.complete')
        if not complete:
            self.assertTrue(self.page.locator('[data-start="rivers"]').is_disabled())
            self.assertIn('noch nicht verfügbar',self.page.locator('#home-data-note').inner_text())
        self.chapter('districts');self.page.locator('#city-scope').select_option('dd-b1')
        self.page.locator('#taipei-map').scroll_into_view_if_needed()
        point=self.page.locator('.district-shape[data-id="dd-altstadt"]').evaluate('''el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}''')
        self.page.touchscreen.tap(point['x'],point['y']);self.assertIn('Altstadt',self.page.locator('#map-detail').inner_text())
        self.assertEqual(self.page.locator('.district-shape[data-id="dd-altstadt"]').evaluate('el=>getComputedStyle(el).webkitTapHighlightColor'),'rgba(0, 0, 0, 0)')
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.screenshot(path='/workspace/duesseldorf-mobile.png',full_page=True)
