import unittest
import analyser.velocity as velocity
import pandas as pd
import os


class VelocityTests(unittest.TestCase):
    # check if exceeded_velocity function makes good csv file
    def test_exceeded_velocity(self):
        velocity.exceeded_velocity(50, 'locations20_40.csv', 'velocity_exceeded.csv', 'meta_data.csv')
        self.assertTrue(os.path.isfile('data\\velocity_exceeded.csv'))
        velocity_exceeded = pd.read_csv('data\\velocity_exceeded.csv')
        self.assertEqual(velocity_exceeded.shape[1], 8)
        # check if there are no NaN values
        self.assertFalse(velocity_exceeded.isnull().values.any())
        # check if there are no duplicates
        self.assertFalse(velocity_exceeded.duplicated().any())
        # check if there are no rows with velocity less than 50
        mask = velocity_exceeded.apply(lambda row: row['velocity'] > 50, axis=1)
        self.assertTrue(mask.all())


if __name__ == '__main__':
    unittest.main()
