import unittest
import analyser.buses_in_districts as buses_in_districts
import pandas as pd
import os


class BusesInDistrictsTests(unittest.TestCase):
    # check if buses_in_districts function makes good csv file
    def test_buses_in_districts(self):
        buses_in_districts.buses_in_districts('buses_locations_with_district.csv')
        self.assertTrue(os.path.isfile('data\\buses_in_districts.csv'))
        buses_in_districts_df = pd.read_csv('data\\buses_in_districts.csv')
        self.assertEqual(buses_in_districts_df.shape[1], 2)
        # check if there are no NaN values
        self.assertFalse(buses_in_districts_df.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(buses_in_districts_df.duplicated().any())

if __name__ == '__main__':
    unittest.main()
