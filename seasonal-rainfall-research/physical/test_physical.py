"""Synthetic tests for coordinate and CPC accumulation-day calculations."""
import unittest
import numpy as np,pandas as pd
from scipy.spatial.distance import cdist
from physical_analysis import coords3,rainfall_day
class PhysicalTests(unittest.TestCase):
 def test_cpc_reporting_day_edges(self):
  t=pd.Series(pd.to_datetime(['2016-08-12 11:59:00','2016-08-12 12:00:00','2016-08-12 12:01:00']))
  self.assertEqual(list(rainfall_day(t).dt.strftime('%Y-%m-%d')),['2016-08-12','2016-08-12','2016-08-13'])
 def test_distance_zero_and_quarter_equator(self):
  x=coords3(np.array([0,90]),np.array([0,0]));d=cdist(x,x);self.assertAlmostEqual(d[0,0],0);self.assertAlmostEqual(d[0,1],np.sqrt(2))
if __name__=='__main__':unittest.main()
