"""Sarlat: localized visitor-only elements must preserve owner booking, payments and QR."""
import re,subprocess,shutil,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"index.html").read_text(encoding="utf-8")
JS=(ROOT/"assets/digiy-sarlat-wo-zh-visitor.js").read_text(encoding="utf-8")
class Test(unittest.TestCase):
 def test_visible_entries(self):
  self.assertIn('id="digiySarlatLanguages"',HTML)
  for lang in ("fr","wo","zh"):self.assertIn('data-lang="'+lang+'"',HTML)
  self.assertIn('id="digiySarlatTranslationNote"',HTML)
  self.assertIn("assets/digiy-sarlat-wo-zh-visitor.js",HTML)
  self.assertIn("lang==='zh'?'zh-CN':lang",JS)
 def test_preserve_business_flows(self):
  for item in ("masterUnitId","DIGIY_SYNC_PUBLIC_LOC","requestForm","waDirect","copyPay","digiyOwnerOpen","publicHeroPrice","publicSummaryPrice","78 €","Sendwave","qr"):
   self.assertIn(item.lower(),HTML.lower())
  self.assertNotIn('fetch(',JS)
  self.assertNotIn('supabase',JS.lower())
  self.assertIn("if(!original.has(selector))original.set(selector,el.textContent)",JS)
 def test_at_least_60_sections_localized(self):
  self.assertGreater(JS.count('"#'),48)
  self.assertIn('"#reservation h2"',JS)
  self.assertIn('"#contact h2"',JS)
  self.assertIn('"#official h2"',JS)
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_valid_javascript(self):
  p=subprocess.run(["node","--check",str(ROOT/"assets/digiy-sarlat-wo-zh-visitor.js")],capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stderr)
if __name__=="__main__":unittest.main()
