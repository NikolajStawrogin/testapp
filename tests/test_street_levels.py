"""Ten-street curricula: lengths, deterministic boundaries and user progression."""
from pathlib import Path
import hashlib,json,math,subprocess,unittest
import test_regions as fixtures
from flow_helpers import GuidedFlow
ROOT=Path(__file__).resolve().parents[1]

def read(name):return json.loads((ROOT/name).read_text().split('=',1)[1].strip().removesuffix(';'))

class StreetLevelDataTests(unittest.TestCase):
    def test_metadata_covers_all_whole_streets_and_matches_inputs(self):
        for region in ['duesseldorf','taipei']:
            metric=read(f'data/levels-{region}.js')
            for name,sha in metric['sourceSha256'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)
            if region=='duesseldorf':features=read('data/duesseldorf.js')['streets']['features']
            else:
                raw=read('data/streets.js');parents=read('data/street-parents.js');replaced=set(parents['replacedIds'])
                features=[f for f in raw['features'] if f['id'] not in replaced]+parents['features']
            self.assertEqual(set(metric['streets']),{f['id'] for f in features if f['unit']=='street'})
            for row in metric['streets'].values():
                self.assertGreaterEqual(row['length'],0)
                self.assertTrue(all(isinstance(v,int) and v>=0 for v in row['districts'].values()))
    def test_parallel_ways_are_not_simply_added(self):
        data=read('data/duesseldorf.js');metric=read('data/levels-duesseldorf.js')
        sy=111320;sx=sy*math.cos(math.radians(51.23))
        for name in ['Heidelberger Straße','Danziger Straße','Münchener Straße']:
            street=next(f for f in data['streets']['features'] if f['nameZh']==name)
            total=sum(math.hypot((b[0]-a[0])*sx,(b[1]-a[1])*sy) for part in street['geometry']['coordinates'] for a,b in zip(part,part[1:]))
            measured=metric['streets'][street['id']]['length']
            self.assertLess(measured,total*(.8 if name=='Heidelberger Straße' else .55),name);self.assertGreater(measured,total*.3,name)
    def test_curriculum_pagination_ties_and_area_ranking(self):
        script=r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');const ctx={window:{}};
vm.runInNewContext(fs.readFileSync('street-levels.js','utf8'),ctx);const api=ctx.window.StreetLevels;
const features=Array.from({length:21},(_,i)=>({id:String(i).padStart(2,'0')}));
const data={streets:Object.fromEntries(features.map((f,i)=>[f.id,{length:100-i,districts:{a:i+1,b:50-i},cities:{city:100-i}}]))};
const all=api.rank(features,data,['a','b'],['a','b']);assert.equal(all[0].feature.id,'00');
const area=api.rank(features,data,['a'],['a','b']);assert.equal(area[0].feature.id,'20');
const first=api.slice(all,1),second=api.slice(all,2),last=api.slice(all,999),review=api.slice(all,2,true);
assert.equal(first.fresh.length,10);assert.equal(second.fresh.length,10);assert.equal(last.fresh.length,1);assert.equal(last.level,3);
assert.equal(new Set([...first.fresh,...second.fresh,...last.fresh].map(r=>r.feature.id)).size,21);
assert.equal(review.active.length,20);assert.equal(api.slice([],1).total,0);
assert.equal(api.areaKey(['a','b']),api.areaKey(['b','a']));
const ties={streets:{b:{length:1,districts:{},cities:{}},a:{length:1,districts:{},cities:{}}}};
assert.equal(api.rank([{id:'b'},{id:'a'}],ties,[],[])[0].feature.id,'a');
'''
        subprocess.run(['node','-e',script],cwd=ROOT,check=True,capture_output=True)

class StreetLevelBrowserTests(GuidedFlow, unittest.TestCase):
    setUpClass=classmethod(fixtures.RegionBrowserTests.setUpClass.__func__)
    tearDownClass=classmethod(fixtures.RegionBrowserTests.tearDownClass.__func__)
    setUp=fixtures.RegionBrowserTests.setUp
    tearDown=fixtures.RegionBrowserTests.tearDown
    open=fixtures.RegionBrowserTests.open
    chapter=fixtures.RegionBrowserTests.chapter
    def ids(self):return self.page.locator('#street-picker .street-choice').evaluate_all('nodes=>nodes.map(n=>n.dataset.streetId)')
    def scope(self,value):
        self.go_step(1);self.page.locator('#city-scope').select_option(value);self.go_step(2)
    def start(self,area='dd-eller'):
        self.open('duesseldorf');self.chapter('streets');self.scope(area)
    def test_default_batches_area_memory_city_and_sorting(self):
        self.start();self.assertEqual(self.page.locator('#street-learning-path').input_value(),'levels')
        first=self.ids();self.assertEqual(len(first),10);self.assertEqual(len(set(first)),10)
        expected=self.page.evaluate("""()=>window.DUESSELDORF_DATA.streets.features.filter(f=>f.unit==='street'&&f.districtIds.includes('dd-eller')).sort((a,b)=>window.STREET_LEVEL_DATA.streets[b.id].districts['dd-eller']-window.STREET_LEVEL_DATA.streets[a.id].districts['dd-eller']||(a.id<b.id?-1:1)).slice(0,10).map(f=>f.id)""")
        self.assertEqual(first,expected)
        self.page.locator('#level-next').click();second=self.ids();self.assertEqual(len(second),10);self.assertFalse(set(first)&set(second))
        self.scope('dd-wersten');self.assertEqual(self.page.locator('#street-level').input_value(),'1')
        self.scope('all');self.assertEqual(self.page.locator('#street-level').input_value(),'1')
        global_ids=self.ids();self.assertEqual(len(global_ids),10)
        self.page.locator('#street-level').select_option('3')
        self.scope('dd-eller');self.assertEqual(self.page.locator('#street-level').input_value(),'2');self.assertEqual(self.ids(),second)
        self.page.reload();self.page.wait_for_selector('body[data-ready="true"]',state='attached');self.configure_topic('streets');self.go_step(2)
        self.assertEqual(self.page.locator('#street-level').input_value(),'2')
        self.scope('all');self.assertEqual(self.page.locator('#street-level').input_value(),'3')
    def test_review_and_last_partial_level_cover_every_street_once(self):
        self.start();first=self.ids();self.page.locator('#level-next').click();self.page.locator('#level-review').check()
        self.assertEqual(len(self.ids()),20);self.assertTrue(set(first).issubset(self.ids()))
        self.page.locator('#level-review').uncheck();total=self.page.locator('#street-level option').count();seen=[]
        for level in range(1,total+1):
            self.page.locator('#street-level').select_option(str(level));batch=self.ids()
            self.assertLessEqual(len(batch),10);self.assertTrue(batch);self.assertFalse(set(batch)&set(seen));seen.extend(batch)
        expected=self.page.evaluate("window.DUESSELDORF_DATA.streets.features.filter(f=>f.unit==='street'&&f.districtIds.includes('dd-eller')).length")
        self.assertEqual(len(seen),expected);self.assertTrue(self.page.locator('#level-next').is_disabled())
    def test_quiz_progress_next_level_and_no_label_answer_hints(self):
        self.start();first=set(self.ids());self.finish_setup('quiz')
        answered=set()
        for _ in range(10):
            self.assertEqual(self.page.locator('.street-label:visible').count(),0)
            name=self.page.locator('#question-name').inner_text()
            id=self.page.evaluate('(name)=>window.DUESSELDORF_DATA.streets.features.find(f=>f.nameZh===name).id',name)
            self.assertIn(id,first);self.assertNotIn(id,answered);answered.add(id)
            self.page.locator(f'.street-shape[data-id="{id}"]').focus();self.page.keyboard.press('Enter')
            self.assertIn('Exactly right',self.page.locator('#feedback').inner_text());self.page.locator('#next-button').click()
        self.assertIn('10 / 10',self.page.locator('#result-score').inner_text());self.assertTrue(self.page.locator('#next-street-level').is_visible())
        self.page.locator('#next-street-level').click();self.wait_idle();self.assertIn('Level 2',self.page.locator('#question-city').inner_text())
        self.page.locator('#session-end').click();self.go_step(2);self.assertFalse(set(self.ids())&first)
        self.page.locator('#level-previous').click();self.assertIn('10 of 10',self.page.locator('#street-level-progress').inner_text())
        self.page.locator('#level-next').click();self.open_progress()
        self.page.locator('#delete-progress').click();self.page.locator('#delete-confirm').click()
        self.page.locator('[aria-label="Close progress"]').click();self.go_step(2)
        self.assertEqual(self.page.locator('#street-level').input_value(),'1')
        self.assertIn('0 of 10',self.page.locator('#street-level-progress').inner_text())
    def test_free_search_and_exclusions_do_not_repartition_levels(self):
        self.start();first=self.ids();self.page.locator('#street-learning-path').select_option('free')
        self.page.locator('#street-search').fill('Gumbert');self.page.wait_for_timeout(180)
        self.page.locator('#street-select-all').click();self.assertIn('0 /',self.page.locator('#street-selection-count').inner_text())
        self.page.locator('#street-learning-path').select_option('levels');self.assertEqual(self.ids(),first)
        self.assertEqual(self.page.locator('#street-picker input:checked').count(),10)
        self.go_step(1);self.page.locator('#select-all').click();self.assertTrue(self.page.locator('#start-button').is_disabled());self.assertTrue(self.page.locator('#street-level').is_disabled())
    def test_taipei_and_new_taipei_have_whole_street_levels(self):
        self.open('taipei');self.chapter('streets')
        for city in ['taipei','new-taipei']:
            self.scope(city);ids=self.ids();self.assertEqual(len(ids),10)
            self.assertTrue(self.page.evaluate('(ids)=>ids.every(id=>window.TAIPEI_STREETS.features.find(f=>f.id===id).unit==="street")',ids))
            self.page.locator('#level-next').click();self.assertFalse(set(ids)&set(self.ids()))
        self.scope('taipei');self.assertEqual(self.page.locator('#street-level').input_value(),'2')
        self.scope('all')
        last=self.page.locator('#street-level option').last.get_attribute('value')
        self.page.locator('#street-level').select_option(last)
        self.finish_setup('explore');self.page.locator('#zoom-reset').click()
        self.assertEqual(self.page.locator('.street-shape:not(.is-context)').count(),len(self.ids()))
    def test_mobile_level_is_visible_after_start_and_backup_restores_positions(self):
        self.context.close();self.context=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        self.context.add_init_script("try { localStorage.setItem('stadt-kennen.ui-language.v1', 'en'); } catch {}")
        self.page=self.context.new_page();self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.on('request',lambda r:self.requests.append(r.url))
        self.start();self.page.locator('#level-next').tap()
        self.page.locator('#menu-toggle').tap();self.page.locator('[data-nav="progress"]').tap()
        with self.page.expect_download() as item:
            self.page.locator('#export-progress').click()
        payload=json.loads(Path(item.value.path()).read_text());self.assertIn(2,payload['streetLearning']['levels'].values())
        self.page.locator('[aria-label="Close progress"]').click();self.page.locator('#level-previous').tap()
        self.page.locator('[data-nav="progress"]').evaluate('el=>el.click()')
        self.page.locator('#import-progress').set_input_files({'name':'levels.json','mimeType':'application/json','buffer':json.dumps(payload).encode()})
        self.page.locator('#confirm-import').click();self.page.locator('[aria-label="Close progress"]').click();self.go_step(2)
        self.assertEqual(self.page.locator('#street-level').input_value(),'2')
        self.finish_setup('quiz')
        box=self.page.locator('#mobile-question').bounding_box();self.assertGreaterEqual(box['y'],0);self.assertLess(box['y']+box['height'],844)
        self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        self.page.screenshot(path='/workspace/street-levels-mobile.png',full_page=True)
