"""Guided preparation, map-only play, busy states and history navigation."""
import unittest
import test_browser as fixtures
from flow_helpers import GuidedFlow

class GuidedFlowTests(GuidedFlow,unittest.TestCase):
    setUpClass=classmethod(fixtures.BrowserTests.setUpClass.__func__)
    tearDownClass=classmethod(fixtures.BrowserTests.tearDownClass.__func__)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1050})
        self.context.add_init_script("localStorage.setItem('stadt-kennen.ui-language.v1','en')")
        self.page=self.context.new_page();self.errors=[];self.requests=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.on('request',lambda r:self.requests.append(r.url))
    def tearDown(self):
        self.assertEqual(self.errors,[])
        self.assertFalse(any(u.startswith(('http:','https:'))and not u.startswith(self.url)for u in self.requests))
        self.context.close()
    def open(self,region='duesseldorf'):
        self.page.goto(self.url+'?region='+region);self.page.wait_for_selector('body[data-ready="true"]',state='attached')
    def test_questions_before_map_validation_review_and_edit(self):
        self.open();self.page.locator('[data-start="streets"]').click()
        self.assertFalse(self.page.locator('#practice-view').is_visible())
        self.assertIn('Where',self.page.locator('#wizard-title').inner_text())
        self.assertEqual(self.page.locator('.street-shape').count(),0,'Street geometry must wait until play')
        self.go_step(1);self.page.locator('#select-all').click();self.assertTrue(self.page.locator('#wizard-next').is_disabled())
        self.assertTrue(self.page.locator('#wizard-validation').is_visible())
        self.page.locator('#city-scope').select_option('dd-eller');self.go_step(2)
        self.page.locator('#street-level').select_option('2');self.page.locator('[data-mode="quiz"]').click()
        self.go_step(3);self.page.locator('#show-metro').uncheck();self.page.locator('#show-river-labels').uncheck();self.go_step(4)
        self.assertIn('Eller',self.page.locator('#wizard-review').inner_text());self.assertIn('Level 2',self.page.locator('#wizard-review').inner_text())
        self.assertNotIn('Rail lines',self.page.locator('#wizard-review').inner_text())
        self.assertFalse(self.page.locator('#practice-view').is_visible())
        self.page.screenshot(path='/workspace/guided-setup-review.png',full_page=True)
        self.finish_setup();self.assertFalse(self.page.locator('#setup-view').is_visible())
        self.assertFalse(self.page.locator('.control-panel').is_visible());self.assertEqual(self.page.locator('#city-scope:visible').count(),0)
        self.assertIn('Level 2',self.page.locator('#question-city').inner_text())
        self.assertGreater(self.page.locator('.map-panel').bounding_box()['width'],1100)
        self.page.screenshot(path='/workspace/guided-game-final.png',full_page=True)
    def test_back_forward_and_reload_do_not_skip_preparation(self):
        self.open();self.configure_topic('districts');self.page.locator('#city-scope').select_option('dd-eller');self.finish_setup('quiz')
        self.assertTrue(self.page.locator('#practice-view').is_visible());self.page.go_back()
        self.assertTrue(self.page.locator('#setup-view').is_visible());self.assertFalse(self.page.locator('#practice-view').is_visible())
        self.assertEqual(self.page.locator('#city-scope').input_value(),'dd-eller')
        self.page.go_forward();self.assertTrue(self.page.locator('#setup-view').is_visible())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertFalse(self.page.locator('#practice-view').is_visible());self.assertTrue(self.page.locator('#home-view').is_visible())
    def test_language_busy_screen_paints_before_slow_map_work(self):
        self.open();self.configure_topic('streets');self.page.locator('#city-scope').select_option('dd-eller');self.finish_setup('quiz')
        name=self.page.locator('#question-name').inner_text();zoom=self.page.locator('#zoom-level').inner_text()
        trace=self.page.evaluate('''async()=>{
            let painted=false;const entries=[];const overlay=document.querySelector('#chapter-loading');
            const observer=new MutationObserver(()=>{if(!overlay.hidden)requestAnimationFrame(()=>{painted=true})});
            observer.observe(overlay,{attributes:true,attributeFilter:['hidden']});
            I18n.subscribe(()=>{entries.push({painted,visible:!overlay.hidden,modal:overlay.open,busy:document.body.getAttribute('aria-busy')});const end=performance.now()+150;while(performance.now()<end){}});
            const work=I18n.setLanguage('zh-Hant');const immediate=!overlay.hidden;
            const cancel=new Event('cancel',{cancelable:true});overlay.dispatchEvent(cancel);const protectedStatus=cancel.defaultPrevented&&overlay.open;
            await work;observer.disconnect();return {immediate,protectedStatus,entries,done:overlay.hidden,inert:document.querySelector('main').inert};
        }''')
        self.assertTrue(trace['immediate']);self.assertTrue(trace['protectedStatus']);self.assertTrue(trace['entries'][0]['painted']);self.assertTrue(trace['entries'][0]['modal'])
        self.assertEqual(trace['entries'][0]['busy'],'true');self.assertTrue(trace['done']);self.assertFalse(trace['inert'])
        self.assertEqual(self.page.locator('#question-name').inner_text(),name);self.assertEqual(self.page.locator('#zoom-level').inner_text(),zoom)
        self.assertIn('在地圖上',self.page.locator('#question-instruction').inner_text())
    def test_place_name_switch_has_busy_screen_above_settings_dialog(self):
        self.open('taipei');self.configure_topic('districts');self.page.locator('#city-scope').select_option('taipei');self.finish_setup('quiz')
        self.open_settings()
        observed=self.page.evaluate('''async()=>{
            const select=document.querySelector('#language');select.value='en';select.dispatchEvent(new Event('change',{bubbles:true}));
            const overlay=document.querySelector('#chapter-loading');const result={shown:!overlay.hidden,modal:overlay.open};
            while(!overlay.hidden)await new Promise(resolve=>setTimeout(resolve,30));return result;
        }''')
        self.assertTrue(observed['shown']);self.assertTrue(observed['modal']);self.assertTrue(self.page.locator('#settings-dialog').is_visible())
        self.close_dialog('settings');self.assertIn('Dist.',self.page.locator('#question-name').inner_text())
        self.assertTrue(self.page.locator('#wizard-display-slot #display-settings').count())
    def test_mobile_questions_and_game_do_not_show_sidebar_or_overflow(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.page=self.context.new_page();self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.open()
        self.configure_topic('streets');self.page.locator('#city-scope').select_option('dd-wersten');self.go_step(2)
        self.page.screenshot(path='/workspace/guided-setup-mobile.png',full_page=True)
        self.finish_setup('quiz')
        box=self.page.locator('#mobile-question').bounding_box();self.assertGreaterEqual(box['y'],0);self.assertLess(box['y']+box['height'],844)
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.assertFalse(self.page.locator('#session-panel').is_visible());self.assertFalse(self.page.locator('#display-settings').is_visible())
        self.page.screenshot(path='/workspace/guided-game-mobile.png',full_page=True)
    def test_river_topic_stays_river_only_after_area_change(self):
        self.open();self.configure_topic('rivers');self.page.locator('#city-scope').select_option('dd-eller')
        self.assertFalse(self.page.locator('#wizard-area-details').is_visible());self.finish_setup('quiz')
        self.assertIn('river',self.page.locator('#question-instruction').inner_text())
        self.assertFalse(self.page.locator('#show-rivers').is_enabled())
        self.page.locator('#reveal-button').click();self.assertIn('green',self.page.locator('#feedback').inner_text())
        self.page.locator('#next-button').click();self.assertTrue(self.page.locator('#results-panel').is_visible())
        self.assertFalse(self.page.locator('.map-panel').is_visible())

    def test_busy_state_recovers_after_a_failed_update(self):
        self.open()
        result=self.page.evaluate("""async()=>{
            let caught=false;try{await I18n.runBusy(()=>{throw new Error('controlled test failure')})}catch{caught=true}
            return {caught,hidden:document.querySelector('#chapter-loading').hidden,open:document.querySelector('#chapter-loading').open,inert:document.querySelector('main').inert,busy:document.body.hasAttribute('aria-busy'),disabled:document.querySelector('#ui-language-toggle').disabled};
        }""")
        self.assertTrue(result['caught']);self.assertTrue(result['hidden']);self.assertFalse(any(result[key]for key in ['open','inert','busy','disabled']))
