import unittest
import weather
import weather_test_data

class TestCreateReport(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_report(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {"total" : 2, "dry" : 1, "rainy" : 1, "ratio" : 0.5})

if __name__ == '__main__':
    unittest.main()