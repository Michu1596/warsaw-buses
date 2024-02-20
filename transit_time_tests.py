import unittest
import analyser.transit_time as transit_time
import pandas as pd
import os
from analyser import distance2


class TransitTimeTest(unittest.TestCase):
    def test_buses_on_bus_stops(self):
        transit_time.buses_on_bus_stops('locations20_40.csv', '180', 0.10)
        self.assertTrue(os.path.isfile('data\\buses_on_stops_simplified180.csv'))
        buses_on_stops = pd.read_csv('data\\buses_on_stops_simplified180.csv')
        self.assertEqual(buses_on_stops.shape[1], 10)
        # check if there are no NaN values
        self.assertFalse(buses_on_stops.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(buses_on_stops.duplicated().any())
        # check if there are no rows with distance greater than 0.10 km
        mask = buses_on_stops.apply(lambda row: distance2(row['dl_geo_stop'] - row['dl_geo_bus'],
                                        row['szer_geo_stop'] - row['szer_geo_bus']) < 0.10, axis=1)
        self.assertTrue(mask.all())

    def test_calculate_transit_time(self):
        # check if calculate_transit_time function makes good csv file
        transit_time.calculate_transit_time('180')
        self.assertTrue(os.path.isfile('data\\transit_time180.csv'))
        transit_time180 = pd.read_csv('data\\transit_time180.csv')
        self.assertEqual(transit_time180.shape[1], 8)
        # check if there are no NaN values
        self.assertFalse(transit_time180.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(transit_time180.duplicated().any())
        # check if time_diff is less than 60
        mask = transit_time180.apply(lambda row: abs(row['time_diff']) < 60, axis=1)
        self.assertTrue(mask.all())



if __name__ == '__main__':
    unittest.main()
