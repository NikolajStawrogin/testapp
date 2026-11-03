"""Validate the exported single-file app with no accompanying files or network."""
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import subprocess
import sys
import tempfile
import unittest
import test_browser as fixtures

class StandaloneRegionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=tempfile.TemporaryDirectory(prefix='stadt-offline-')
        cls.root=Path(cls.directory.name)
        subprocess.run([sys.executable,str(fixtures.ROOT/'tools/export_standalone.py'),'--output',str(cls.root/'index.html')],check=True,capture_output=True)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(fixtures.QuietHandler,directory=str(cls.root)))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}/'
        from playwright.sync_api import sync_playwright
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.playwright.stop();cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.directory.cleanup()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.page=self.context.new_page();self.errors=[];self.requests=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.on('request',lambda r:self.requests.append(r.url))
    def tearDown(self):
        self.assertEqual(self.errors,[])
        self.assertFalse(any('.js' in url or '.css' in url or '/data/' in url for url in self.requests),self.requests)
        self.context.close()
    def open(self,region):
        self.page.goto(self.url+'?region='+region)
        self.page.wait_for_selector('body[data-ready="true"]',state='attached')
        self.context.set_offline(True)
    def test_dusseldorf_mobile_river_round_and_transit_filters_offline(self):
        self.open('duesseldorf')
        self.page.locator('[data-start="rivers"]').tap();self.page.locator('#chapter-loading').wait_for(state='hidden')
        self.assertEqual(self.page.locator('.metro-line').count(),26)
        self.page.locator('[data-transport-kind="suburban"]').uncheck()
        self.assertEqual(self.page.locator('.metro-line[data-kind="suburban"]:visible').count(),0)
        self.page.locator('[data-mode="quiz"]').tap();self.page.locator('#start-button').tap()
        for _ in range(6):
            self.page.locator('#mobile-reveal').tap()
            self.assertTrue(self.page.locator('#map-detail').is_visible())
            self.page.locator('#mobile-next').tap()
        self.assertTrue(self.page.locator('#results-panel').is_visible())
        self.assertEqual(self.page.evaluate('JSON.parse(localStorage.getItem("duesseldorf-kennen.progress.v1")).rounds'),1)
    def test_taipei_mobile_street_quiz_offline(self):
        self.open('taipei')
        self.page.locator('[data-start="streets"]').tap();self.page.locator('#chapter-loading').wait_for(state='hidden')
        self.page.locator('#city-scope').select_option('taipei')
        self.page.locator('[name="street-unit"][value="section"]').uncheck()
        self.page.locator('#street-search').fill('忠孝東路')
        self.page.wait_for_function("document.querySelectorAll('#street-picker input').length===1")
        self.page.locator('[data-mode="quiz"]').tap();self.page.locator('#start-button').tap()
        self.page.locator('#mobile-reveal').tap()
        self.assertTrue(self.page.locator('.street-solution').get_attribute('d'))
        self.page.locator('#mobile-next').tap()
        self.assertTrue(self.page.locator('#results-panel').is_visible())
