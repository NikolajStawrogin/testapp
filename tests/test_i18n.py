"""Interface languages, in-place switching, persistence and local delivery."""
import json
from pathlib import Path
import re
import unittest
import test_browser as fixtures
from flow_helpers import GuidedFlow

ROOT=fixtures.ROOT
class TranslationDataTests(unittest.TestCase):
    def test_catalog_complete_placeholders_and_traditional_language_names(self):
        text=(ROOT/'i18n.js').read_text()
        catalog=json.loads(text.split('const messages = ',1)[1].split(';\n  const sources',1)[0])
        keys=set(re.findall(r'data-i18n(?:-[a-z-]+)?="([^"]+)"',(ROOT/'index.html').read_text()))
        for file in ['app.js','bootstrap.js','region-ui.js','street-map.js']:
            keys.update(re.findall(r'\bt\("([^"]+)"', (ROOT/file).read_text()))
        self.assertFalse(keys-set(catalog),keys-set(catalog))
        for key,(source,en,zh) in catalog.items():
            self.assertTrue(en,key);self.assertTrue(zh,key)
            self.assertEqual(set(re.findall(r'\{\d+\}',en)),set(re.findall(r'\{\d+\}',zh)),key)
        self.assertEqual(catalog['mandarin'][1:],['Mandarin','國語'])
        self.assertFalse(any(re.search(r'\bChinese\b',row[1])for row in catalog.values()))

class InterfaceLanguageTests(GuidedFlow, unittest.TestCase):
    setUpClass=classmethod(fixtures.BrowserTests.setUpClass.__func__)
    tearDownClass=classmethod(fixtures.BrowserTests.tearDownClass.__func__)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1440,'height':1050},locale='de-DE')
        self.page=self.context.new_page();self.errors=[];self.external=[]
        self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.page.on('request',lambda request:self.external.append(request.url) if request.url.startswith(('http:','https:'))and not request.url.startswith(self.url)else None)
    def tearDown(self):
        self.assertEqual(self.errors,[]);self.assertEqual(self.external,[]);self.context.close()
    def open(self,region=''):
        self.page.goto(self.url+(''if not region else '?region='+region))
        if region:self.page.wait_for_selector('body[data-ready="true"]',state='attached')
    def switch(self,language):
        self.page.locator('#ui-language-toggle').click();self.page.locator(f'[data-ui-language="{language}"]').click()
        self.wait_idle();self.assertEqual(self.page.locator('html').get_attribute('lang'),language)
    def chapter(self,topic):
        self.configure_topic(topic)
    def test_first_visit_traditional_mandarin_and_language_menu_keyboard(self):
        self.open();self.assertEqual(self.page.locator('html').get_attribute('lang'),'zh-Hant')
        self.assertEqual(self.page.locator('#page-heading').inner_text(),'你想認識哪座城市？')
        self.assertTrue(self.page.locator('#ui-language-toggle').is_visible())
        self.page.locator('#ui-language-toggle').focus();self.page.keyboard.press('Enter')
        self.assertEqual(self.page.locator('[data-ui-language="zh-Hant"]').inner_text(),'國語')
        self.page.keyboard.press('Escape');self.assertFalse(self.page.locator('#ui-language-menu').is_visible())
        self.switch('en');self.page.locator('#ui-language-toggle').click()
        self.assertEqual(self.page.locator('[data-ui-language="zh-Hant"]').inner_text(),'Mandarin')
        self.assertEqual(self.page.locator('[data-ui-language="en"]').get_attribute('aria-pressed'),'true')
        self.assertIn('Choose a city',self.page.title())
    def test_language_persists_across_reload_and_cities_without_changing_progress(self):
        self.context.add_init_script("localStorage.setItem('taipei-kennen.settings.v1',JSON.stringify({language:'en'}))")
        self.open();self.switch('en')
        self.page.evaluate("localStorage.setItem('taipei-kennen.progress.v1',JSON.stringify({rounds:4,districts:{daan:{attempts:3,correct:2}}}))")
        before=self.page.evaluate("localStorage.getItem('taipei-kennen.progress.v1')")
        self.page.locator('[data-region="duesseldorf"]').click();self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertEqual(self.page.locator('html').get_attribute('lang'),'en');self.assertIn('Learn streets',self.page.locator('[data-start="streets"]').inner_text())
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.assertEqual(self.page.locator('html').get_attribute('lang'),'en')
        self.switch('zh-Hant');self.open_menu();self.page.locator('.region-change').click();self.page.locator('[data-region="taipei"]').click()
        self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.assertEqual(self.page.locator('html').get_attribute('lang'),'zh-Hant');self.assertIn('認識街道',self.page.locator('[data-start="streets"]').inner_text())
        self.assertEqual(self.page.locator('#language').input_value(),'en')
        self.assertEqual(self.page.evaluate("localStorage.getItem('taipei-kennen.progress.v1')"),before)
    def test_switch_mid_quiz_keeps_answer_question_and_name_settings(self):
        self.open('taipei');self.chapter('districts');self.page.locator('#city-scope').select_option('taipei')
        self.page.locator('#select-all').click();self.page.locator('#district-picker input[value="zhongzheng"]').check()
        self.finish_setup('quiz')
        name=self.page.locator('#question-name').inner_text();language=self.page.locator('#language').input_value()
        self.switch('en');self.assertEqual(self.page.locator('#question-name').inner_text(),name)
        self.assertIn('Find this district',self.page.locator('#question-instruction').inner_text())
        self.page.locator('.district-shape[data-id="zhongzheng"]').focus();self.page.keyboard.press('Enter')
        self.assertIn('Exactly right!',self.page.locator('#feedback').inner_text());self.switch('zh-Hant')
        self.assertIn('答對了',self.page.locator('#feedback').inner_text());self.assertIn('萬華區以東',self.page.locator('#feedback').inner_text())
        self.assertEqual(self.page.locator('#language').input_value(),language)
        self.page.locator('#next-button').click();self.assertIn('1 / 1',self.page.locator('#result-score').inner_text())
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('taipei-kennen.progress.v1')).districts.zhongzheng.correct"),1)
    def test_mobile_street_round_switch_keeps_level_view_and_original_names(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.page=self.context.new_page();self.page.on('pageerror',lambda error:self.errors.append(str(error)))
        self.open('duesseldorf');self.chapter('streets');self.page.locator('#city-scope').select_option('dd-eller')
        self.go_step(2);self.page.locator('#level-next').tap();self.finish_setup('cards')
        name=self.page.locator('#question-name').inner_text();self.page.locator('#mobile-reveal').tap()
        zoom=self.page.locator('#zoom-level').inner_text();self.switch('en')
        self.assertEqual(self.page.locator('#question-name').inner_text(),name);self.assertIn('Level 2',self.page.locator('#question-city').inner_text())
        self.assertEqual(self.page.locator('#zoom-level').inner_text(),zoom);self.assertIn('Whole named street',self.page.locator('#feedback').inner_text());self.assertIn('Map/rivers:',self.page.locator('.map-footer').inner_text())
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.locator('#ui-language-toggle').scroll_into_view_if_needed();self.page.screenshot(path='/workspace/interface-english-mobile.png')
        self.switch('zh-Hant');self.assertIn('地圖／河流',self.page.locator('.map-footer').inner_text());self.assertIn('第 2 級',self.page.locator('#street-level option:checked').inner_text());self.page.locator('#ui-language-toggle').scroll_into_view_if_needed();self.page.screenshot(path='/workspace/interface-mandarin-mobile.png')
    def test_invalid_backup_has_localised_error(self):
        self.open('taipei');self.page.locator('#progress-open').click()
        self.page.locator('#import-progress').set_input_files({'name':'broken.json','mimeType':'application/json','buffer':b'{'})
        self.page.wait_for_function("document.querySelector('#toast').textContent.includes('有效')")
        self.assertIn('不是有效的學習進度備份',self.page.locator('#toast').inner_text())
        self.assertNotIn('JSON',self.page.locator('#toast').inner_text())

    def test_help_sources_settings_and_storage_unavailable(self):
        self.open('duesseldorf');self.switch('en')
        for dialog,nav,phrase in [('help','help','ten new whole streets'),('settings','settings','Place-name language'),('sources','help','')]:
            self.open_menu();self.page.locator(f'[data-nav="{nav}"]').click()
            if dialog=='sources':self.page.locator('#help-sources').click()
            if phrase:self.assertIn(phrase,self.page.locator('#'+dialog+'-dialog').inner_text())
            self.assertFalse(re.search(r'\b(Straßen|Stadtteile|Quelle|Lernstand|Die|werden)\b',self.page.locator('#'+dialog+'-dialog').inner_text()))
            self.page.locator('#'+dialog+'-dialog .dialog-close').click()
        self.context.add_init_script("Storage.prototype.getItem=function(){throw new Error('blocked')};Storage.prototype.setItem=function(){throw new Error('blocked')}")
        self.open();self.assertEqual(self.page.locator('html').get_attribute('lang'),'zh-Hant');self.switch('en')
        self.assertIn('Which city',self.page.locator('#page-heading').inner_text())
