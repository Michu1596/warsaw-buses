import unittest
import analyser.punctuality as punctuality
import pandas as pd
import os
from analyser import distance2


class TestPunctuality(unittest.TestCase):
    def test_punctuality_of_line(self):
        punctuality.punctuality_of_line('locations20_40.csv', '180', 0.10)
        self.assertTrue(os.path.isfile('data\\buses_on_stops180.csv'))
        buses_on_stops = pd.read_csv('data\\buses_on_stops180.csv')
        self.assertEqual(buses_on_stops.shape[1], 17)
        # # check if there are no NaN values
        self.assertFalse(buses_on_stops.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(buses_on_stops.duplicated().any())
        # check if there are no rows with time difference greater than 1 hour
        buses_on_stops['time_bus'] = pd.to_datetime(buses_on_stops['time_bus'], format='%H:%M:%S').dt.time
        buses_on_stops['time_stop'] = pd.to_datetime(buses_on_stops['time_stop'], format='%H:%M:%S').dt.time
        mask = buses_on_stops.apply(lambda row: abs(row['time_bus'].hour - row['time_stop'].hour) < 1, axis=1)
        self.assertTrue(mask.all())
        # check if there are no rows with distance greater than 0.10 km
        mask = buses_on_stops.apply(lambda row: distance2(row['dl_geo_stop'] - row['dl_geo_bus'],
                                        row['szer_geo_stop'] - row['szer_geo_bus']) < 0.10, axis=1)

    def test_test_punctuality_of_line(self):
        punctuality.test_punctuality_of_line('180', 3)
        self.assertTrue(os.path.isfile('data\\buses_late_or_early180.csv'))
        buses_late_or_early = pd.read_csv('data\\buses_late_or_early180.csv')
        self.assertEqual(buses_late_or_early.shape[1], 16)
        # check if there are no NaN values
        self.assertFalse(buses_late_or_early.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(buses_late_or_early.duplicated().any())
        # check if time_diff is less than 60
        mask = buses_late_or_early.apply(lambda row: abs(row['time_diff']) < 60, axis=1)
        self.assertTrue(mask.all())
