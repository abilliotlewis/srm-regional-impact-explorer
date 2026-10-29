"""Synthetic unit tests for event counting; these inputs are not observations."""
import unittest
import numpy as np
import pandas as pd
from run_regional import objects, counts

class EventTests(unittest.TestCase):
 def test_same_day_distinct_spatial_footprints_vs_time_runs(self):
  x=np.zeros((4,8,8),bool); x[0,0:2,0:2]=True; x[0,6:8,6:8]=True; x[1,1:3,1:3]=True
  d=pd.date_range('2001-06-01',periods=4)
  spatial=objects(x,d,'tracked'); temporal=objects(x,d,'runs')
  self.assertEqual(len(spatial),2); self.assertEqual(len(temporal),1)
  self.assertEqual(spatial.duration_days.max(),2)
 def test_adjacent_dates_and_season_boundary(self):
  x=np.zeros((3,5,5),bool);x[0,1:3,1:3]=True;x[1,1:3,1:3]=True
  d=pd.date_range('2000-12-31',periods=3); e=objects(x,d,'tracked')
  self.assertEqual(len(e),1);self.assertEqual(e.iloc[0].season_year,2001);self.assertEqual(e.iloc[0].season,'DJF')
 def test_one_day_gap_in_runs(self):
  x=np.zeros((4,4,4),bool);x[0,1:3,1:3]=True;x[2,1:3,1:3]=True
  d=pd.date_range('2001-06-01',periods=4)
  self.assertEqual(len(objects(x,d,'runs',gap=1)),1)
  self.assertEqual(len(objects(x,d,'runs',gap=0)),2)

if __name__=='__main__':unittest.main()
