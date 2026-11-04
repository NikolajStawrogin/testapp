"""Region entry, data isolation and Düsseldorf learning regressions."""
import json
import unittest
import test_browser as fixtures

class RegionBrowserTests(unittest.TestCase):
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
    def test_neighborhood_scope_names_and_quiz(self):
        self.open('duesseldorf');self.chapter('districts')
        self.assertEqual(self.page.locator('#district-picker input').count(),50)
        labels=self.page.locator('#city-scope option').all_text_contents()
        self.assertEqual(len(labels),51)
        self.assertIn('Eller',labels);self.assertIn('Wersten',labels)
        self.assertFalse(any('borough' in label for label in labels))
        self.assertFalse(self.page.locator('#area-level-field').is_visible())
        self.assertEqual(self.page.locator('.district-group-title').count(),0)
        self.page.locator('#city-scope').select_option('dd-eller')
        self.assertEqual(self.page.locator('#district-picker input').count(),1)
        self.assertEqual(self.page.locator('#map-title').inner_text(),'Eller')
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#start-button').click()
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Eller')
        self.district_tap('dd-eller');self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())
        self.page.locator('#next-button').click()
        self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertEqual(self.page.locator('#city-scope').input_value(),'dd-eller')
        self.page.locator('#city-scope').select_option('dd-wersten')
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#start-button').click()
        self.assertEqual(self.page.locator('#question-name').inner_text(),'Wersten')
        self.page.locator('#session-end').click();self.page.locator('#city-scope').select_option('all')
        self.page.locator('#select-all').click()
        for id in ['dd-eller','dd-wersten']:self.page.locator(f'#district-picker input[value="{id}"]').check()
        self.page.locator('#round-size').select_option('all');self.page.locator('#start-button').click()
        questions=set()
        for _ in range(2):
            questions.add(self.page.locator('#question-name').inner_text())
            self.page.locator('#reveal-button').click();self.page.locator('#next-button').click()
        self.assertEqual(questions,{'Eller','Wersten'})
    def test_old_numbered_selection_migrates_to_neighborhoods(self):
        self.open('duesseldorf')
        self.page.evaluate("""() => {
          localStorage.setItem('duesseldorf-kennen.settings.v1',JSON.stringify({datasetVersion:2,view:'practice',areaLevel:'borough',scope:'dd-b8',selected:['dd-bezirk-8']}));
          localStorage.setItem('duesseldorf-kennen.progress.v1',JSON.stringify({rounds:2,districts:{'dd-bezirk-8':{attempts:2,correct:1}}}));
        }""")
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        selected=self.page.locator('#district-picker input:checked').evaluate_all('nodes=>nodes.map(n=>n.value).sort()')
        self.assertEqual(selected,['dd-eller','dd-lierenfeld','dd-unterbach','dd-vennhausen'])
        self.assertEqual(self.page.locator('.district-shape:visible').count(),50)
        self.assertEqual(self.page.evaluate('JSON.parse(localStorage.getItem("duesseldorf-kennen.progress.v1")).rounds'),2)
    def test_street_scope_follows_neighborhood(self):
        self.open('duesseldorf');self.chapter('streets')
        for id in ['dd-eller','dd-wersten']:
            self.page.locator('#city-scope').select_option(id)
            ids=self.page.locator('#street-picker input').evaluate_all('nodes=>nodes.map(n=>n.value)')
            self.assertTrue(ids)
            self.assertTrue(self.page.evaluate('''({ids,area})=>ids.every(id=>window.DUESSELDORF_DATA.streets.features.find(f=>f.id===id).districtIds.includes(area))''',{'ids':ids,'area':id}))
    def test_street_quiz_and_taipei_progress_are_separate(self):
        self.open('duesseldorf')
        self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify({rounds:4,districts:{daan:{attempts:3,correct:2}}}))")
        self.chapter('streets');self.page.locator('#street-learning-path').select_option('free');self.page.locator('#street-search').fill('Königsallee')
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
        self.assertIn('another city',self.page.locator('#toast').inner_text())
        self.assertFalse(self.page.locator('#import-confirmation').is_visible())
    def test_mobile_german_layout_touch_selection_and_pending_data_status(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("try { localStorage.setItem('stadt-kennen.ui-language.v1', 'en'); } catch {}")
        self.page=self.context.new_page();self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.on('request',lambda r:self.requests.append(r.url))
        self.open('duesseldorf');complete=self.page.evaluate('window.DUESSELDORF_DATA.complete')
        if not complete:
            self.assertTrue(self.page.locator('[data-start="rivers"]').is_disabled())
            self.assertIn('not available yet',self.page.locator('#home-data-note').inner_text())
        self.chapter('districts');self.page.locator('#city-scope').select_option('dd-altstadt')
        self.page.locator('#taipei-map').scroll_into_view_if_needed()
        point=self.page.locator('.district-shape[data-id="dd-altstadt"]').evaluate('''el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}''')
        self.page.touchscreen.tap(point['x'],point['y']);self.assertIn('Altstadt',self.page.locator('#map-detail').inner_text())
        self.assertEqual(self.page.locator('.district-shape[data-id="dd-altstadt"]').evaluate('el=>getComputedStyle(el).webkitTapHighlightColor'),'rgba(0, 0, 0, 0)')
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.screenshot(path='/workspace/duesseldorf-mobile.png',full_page=True)

    def river_point(self,id):
        self.page.locator('#taipei-map').scroll_into_view_if_needed()
        return self.page.locator(f'.river-hit[data-id="{id}"]').evaluate("""el=>{
          const p=new DOMPoint(+el.dataset.anchorX,+el.dataset.anchorY).matrixTransform(el.getScreenCTM());return {x:p.x,y:p.y};}""")
    def test_river_quiz_wrong_answer_retry_and_name_visibility(self):
        self.open('duesseldorf');self.chapter('rivers')
        self.assertEqual(self.page.locator('#river-picker input:checked').count(),6)
        self.assertEqual(self.page.locator('#district-picker input:checked').count(),0)
        self.page.locator('#show-river-labels').uncheck()
        self.assertEqual(self.page.locator('.river-label:visible').count(),0)
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#round-size').select_option('all');self.page.locator('#start-button').click()
        rivers=self.page.evaluate('window.DUESSELDORF_DATA.rivers.features');first=None
        for index in range(6):
            name=self.page.locator('#question-name').inner_text();target=next(r for r in rivers if r['nameZh']==name)
            chosen=next(r for r in rivers if r['id']!=target['id']) if index==0 else target
            if index==0:first=target
            point=self.river_point(chosen['id']);self.page.mouse.click(point['x'],point['y'])
            self.assertIn('Not quite yet' if index==0 else 'Exactly right',self.page.locator('#feedback').inner_text())
            self.assertIn(target['nameZh'],self.page.locator('#map-detail').inner_text())
            self.assertIn('is-correct',self.page.locator(f'.river-shape[data-id="{target["id"]}"]').get_attribute('class'))
            self.page.locator('#next-button').click()
        self.assertIn('5 / 6',self.page.locator('#result-score').inner_text())
        self.page.locator('#retry-errors').click();self.assertEqual(self.page.locator('#question-name').inner_text(),first['nameZh'])
        point=self.river_point(first['id']);self.page.mouse.click(point['x'],point['y']);self.page.locator('#next-button').click()
        stats=self.page.evaluate('JSON.parse(localStorage.getItem("duesseldorf-kennen.progress.v1"))')
        self.assertEqual(stats['districts'][first['id']],{'attempts':2,'correct':1})
    def test_transit_kinds_toggle_persist_and_do_not_answer_quiz(self):
        self.open('duesseldorf');self.chapter('districts')
        self.assertEqual(self.page.locator('.metro-line:visible').count(),26)
        self.page.locator('[data-transport-kind="suburban"]').uncheck()
        self.assertEqual(self.page.locator('.metro-line[data-kind="suburban"]:visible').count(),0)
        self.assertEqual(self.page.locator('.metro-line[data-kind="metro"]:visible').count(),12)
        self.page.locator('#metro-legend summary').click();self.assertIn('Schematic',self.page.locator('.metro-legend-note').inner_text())
        self.assertEqual(self.page.locator('.metro-chip').count(),20)
        self.page.locator('[data-mode="quiz"]').click();self.page.locator('#start-button').click()
        self.page.locator('[data-transport-kind="tram"]').uncheck();self.assertFalse(self.page.locator('#feedback').is_visible())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertFalse(self.page.locator('[data-transport-kind="suburban"]').is_checked())
        self.assertFalse(self.page.locator('[data-transport-kind="tram"]').is_checked())
        self.assertEqual(self.page.locator('.metro-line:visible').count(),13)
    def test_previous_dusseldorf_settings_gain_layers_without_losing_progress(self):
        self.open('duesseldorf')
        self.page.evaluate("""() => {
          localStorage.setItem('duesseldorf-kennen.settings.v1',JSON.stringify({datasetVersion:1,view:'home',metro:false,rivers:false,selectedRivers:[],selected:[]}));
          localStorage.setItem('duesseldorf-kennen.progress.v1',JSON.stringify({rounds:3,districts:{'dd-bilk':{attempts:4,correct:3}}}));
        }""")
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertEqual(self.page.locator('#district-picker input:checked').count(),0,'An explicitly empty area selection survives the data upgrade')
        self.chapter('rivers')
        self.assertTrue(self.page.locator('#show-metro').is_checked());self.assertTrue(self.page.locator('#show-rivers').is_checked())
        self.assertEqual(self.page.locator('#river-picker input:checked').count(),6)
        self.assertEqual(self.page.evaluate('JSON.parse(localStorage.getItem("duesseldorf-kennen.progress.v1")).rounds'),3)
    def test_mobile_river_touch_and_map_layers(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("try { localStorage.setItem('stadt-kennen.ui-language.v1', 'en'); } catch {}")
        self.page=self.context.new_page();self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.open('duesseldorf');self.chapter('rivers');self.page.locator('[data-mode="quiz"]').tap();self.page.locator('#start-button').tap()
        name=self.page.locator('#mobile-question-name').inner_text()
        target=self.page.evaluate('(name)=>window.DUESSELDORF_DATA.rivers.features.find(r=>r.nameZh===name)',name)
        p=self.river_point(target['id']);self.page.touchscreen.tap(p['x'],p['y'])
        self.assertIn('Exactly right',self.page.locator('#feedback').inner_text())
        self.assertTrue(self.page.locator('#map-detail').is_visible());self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.screenshot(path='/workspace/duesseldorf-rivers-mobile.png',full_page=True)
