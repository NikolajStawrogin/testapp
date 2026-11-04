"""User-visible selection feedback, loading, gesture work and touch target regressions."""
import unittest
import test_streets_browser as streets
from flow_helpers import GuidedFlow

class MapUXTests(GuidedFlow, unittest.TestCase):
    setUpClass = classmethod(streets.StreetBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(streets.StreetBrowserTests.tearDownClass.__func__)
    setUp = streets.StreetBrowserTests.setUp
    tearDown = streets.StreetBrowserTests.tearDown
    open_practice = streets.StreetBrowserTests.open_practice
    street_mode = streets.StreetBrowserTests.street_mode
    search = streets.StreetBrowserTests.search
    target = streets.StreetBrowserTests.target
    point = streets.StreetBrowserTests.point
    click_street = streets.StreetBrowserTests.click_street

    def test_selection_overlay_scope_and_collapsible_legend(self):
        page = self.page
        self.assertFalse(page.locator('#metro-legend').evaluate('el=>el.open'))
        page.locator('#metro-legend summary').click()
        self.assertTrue(page.locator('.metro-chip').first.is_visible())
        page.locator('#metro-legend summary').click()
        self.assertFalse(page.locator('.metro-chip').first.is_visible())
        self.assertEqual(page.locator('#city-scope:visible').count(), 0)
        self.assertGreaterEqual(page.locator('#game-map-settings').bounding_box()['height'], 44)
        path = page.locator('.district-shape:not(.is-muted)').first
        path.dispatch_event('click')
        # Select using the keyboard so both accessible and pointer feedback are checked.
        path.focus()
        page.keyboard.press('Enter')
        self.assertEqual(path.evaluate('el=>getComputedStyle(el).outlineStyle'), 'none')
        self.assertTrue(page.locator('#map-detail').is_visible())
        detail, stage = [page.locator(selector).bounding_box() for selector in ['#map-detail', '#map-stage']]
        self.assertGreaterEqual(detail['y'], stage['y'])
        self.assertLessEqual(detail['y'] + detail['height'], stage['y'] + stage['height'])

    def test_loading_paints_before_street_preparation_and_zoom_batches_rendering(self):
        page = self.page
        self.street_mode();self.go_step(4)
        shown = page.evaluate("() => {document.querySelector('#start-button').click();return !document.querySelector('#chapter-loading').hidden}")
        self.assertTrue(shown);self.wait_idle()
        page.wait_for_timeout(200)
        result = page.evaluate('''async () => {
          let count=0;
          const observer=new MutationObserver(records=>count+=records.length);
          observer.observe(document.getElementById('street-layer'),{subtree:true,attributes:true,childList:true});
          const before=document.getElementById('map-content').getAttribute('transform');
          for(let i=0;i<12;i++)document.getElementById('zoom-in').click();
          await Promise.resolve();
          const during=count;
          const after=document.getElementById('map-content').getAttribute('transform');
          await new Promise(resolve=>setTimeout(resolve,250));
          observer.disconnect();
          return {during, settled:count, moved:before!==after};
        }''')
        self.assertTrue(result['moved'])
        self.assertEqual(result['during'], 0, 'No street DOM rebuild during a zoom burst')
        self.assertGreater(result['settled'], 0, 'Street details refresh after zoom settles')

    def test_solution_is_above_map_layers_and_finger_can_miss_centerline(self):
        self.street_mode()
        self.search('忠孝東路')
        self.page.locator('[name="street-unit"][value="street"]').uncheck()
        self.finish_setup('quiz')
        target = self.target()
        self.page.locator('#reveal-button').click()
        solution = self.page.locator('.street-solution')
        self.assertEqual(solution.get_attribute('data-id'), target['id'])
        self.assertTrue(solution.get_attribute('d'))
        self.assertGreaterEqual(float(solution.evaluate('el=>getComputedStyle(el).strokeWidth').rstrip('px')), 8)
        self.assertLessEqual(float(self.page.locator('#street-layer').evaluate('el=>getComputedStyle(el).opacity')), .3)
        self.page.screenshot(path='/workspace/taipei-map-ux-desktop.png', full_page=True)
        self.page.set_viewport_size({'width':390,'height':844})
        self.page.locator('#taipei-map').scroll_into_view_if_needed()
        self.assertTrue(self.page.locator('#map-detail').is_visible())
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.screenshot(path='/workspace/taipei-map-ux-mobile.png', full_page=True)
        # Exercise geographic picking at 24 CSS pixels from an isolated street.
        picked = self.page.evaluate('''() => {
          const Native=window.TaipeiStreetLayer;
          const layer=Object.create(Native.prototype);
          const feature={id:'test-road'};
          layer.options={visible:true,pool:new Set(['test-road']),revealed:false};
          let zoom=1;
          layer.root={getScreenCTM:()=>new DOMMatrix().scale(zoom)};
          layer.visible=[{feature,bounds:[0,0,100,0],parts:[[[0,0],[100,0]]]}];
          const normal=[layer.pick(50,24,true),layer.pick(50,24,false)];
          zoom=10;
          return [...normal,layer.pick(50,24,true),layer.pick(50,24,false)];
        }''')
        self.assertEqual(picked, ['test-road', None, 'test-road', None])
