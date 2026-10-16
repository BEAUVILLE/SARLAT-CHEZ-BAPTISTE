import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
URL="https://sarlat-chez-baptiste.digiylyfe.com/"
class SearchDiscovery(unittest.TestCase):
 def test_page(self):
  s=(ROOT/"index.html").read_text(encoding="utf-8")
  self.assertIn('rel="canonical" href="'+URL+'"',s)
  self.assertIn('name="robots" content="index,follow',s)
 def test_sitemap(self):
  root=ET.parse(ROOT/"sitemap.xml").getroot()
  self.assertEqual([x.text for x in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")],[URL])
 def test_robots(self):
  s=(ROOT/"robots.txt").read_text(encoding="utf-8")
  self.assertIn("Sitemap: "+URL+"sitemap.xml",s)
if __name__=="__main__": unittest.main()
