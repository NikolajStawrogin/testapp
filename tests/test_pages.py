"""Verify the static app as served from a GitHub Pages project subdirectory."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import os
import re
import shutil
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class ProjectHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if not urlsplit(self.path).path.startswith("/testapp/"):
            self.send_error(404)
            return
        super().do_GET()

    def translate_path(self, path):
        return super().translate_path(path.removeprefix("/testapp"))


class PagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(ProjectHandler, directory=str(ROOT)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/testapp/"
        cls.playwright = sync_playwright().start()
        executable = os.environ.get("TAIPEI_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome")
        cls.browser = cls.playwright.chromium.launch(executable_path=executable, args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_project_subpath_loads_every_app_asset_and_plays_quiz(self):
        self.assertTrue((ROOT / ".nojekyll").exists())
        errors, responses, external = [], {}, []
        with self.browser.new_context(viewport={"width": 1440, "height": 1100}) as context:
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: responses.update({response.url: response.status}))
            page.on("request", lambda request: external.append(request.url) if request.url.startswith(("http:", "https:")) and not request.url.startswith(self.url) and not request.url.endswith("/favicon.ico") else None)
            self.assertEqual(page.goto(self.url + "?region=taipei").status, 200)
            page.wait_for_selector('body[data-ready="true"]', state="attached")
            self.assertTrue(page.locator("#home-view").is_visible())
            assets = ["styles.css", "bootstrap.js", "region-ui.js", "street-map.js", "app.js", "data/districts.js", "data/metro.js", "data/rivers.js", "data/streets.js", "data/street-parents.js"]
            assets = [asset + "?v=0.10" for asset in assets]
            for asset in assets:
                self.assertEqual(responses.get(self.url + asset), 200, asset)
            page.locator('[data-start="streets"]').click()
            page.locator("#city-scope").select_option("taipei")
            page.locator('[name="street-unit"][value="section"]').uncheck()
            page.locator("#street-search").fill("忠孝東路")
            page.wait_for_function("document.querySelectorAll('#street-picker input').length===1")
            page.locator('[data-mode="quiz"]').click()
            page.locator("#start-button").click()
            self.assertEqual(page.locator("#question-name").inner_text(), "忠孝東路")
            page.locator("#reveal-button").click()
            page.locator("#next-button").click()
            self.assertTrue(page.locator("#results-panel").is_visible())
            progress = page.evaluate("JSON.parse(localStorage.getItem('taipei-kennen.progress.v1'))")
            self.assertEqual(progress["rounds"], 1)
            self.assertEqual(errors, [])
            self.assertEqual(external, [])

    def test_mobile_menu_works_without_accounts_or_external_services(self):
        errors = []
        with self.browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True) as context:
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            self.assertEqual(page.goto(self.url + "?region=taipei").status, 200)
            page.wait_for_selector('body[data-ready="true"]', state="attached")
            page.locator("#menu-toggle").tap()
            page.locator('[data-nav="help"]').tap()
            self.assertTrue(page.locator("#help-dialog").is_visible())
            self.assertFalse(page.evaluate("document.documentElement.scrollWidth>innerWidth"))
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
