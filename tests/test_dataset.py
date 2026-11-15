
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from generate_dataset import build
from validate_dataset import validate
class DatasetTests(unittest.TestCase):
 def test_small_generation_and_integrity(self):
  with tempfile.TemporaryDirectory() as d:
   build(d,250,30,123,"2025-01-01");r=validate(d)
   self.assertTrue(r["valid"],r["errors"]);self.assertEqual(r["counts"]["trips"],250);self.assertEqual(r["counts"]["boarding_events"],500)
 def test_seed_reproducibility(self):
  with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
   build(a,30,10,99);build(b,30,10,99)
   self.assertEqual((Path(a)/"data/raw/trips.csv").read_bytes(),(Path(b)/"data/raw/trips.csv").read_bytes())
if __name__=="__main__":unittest.main()
