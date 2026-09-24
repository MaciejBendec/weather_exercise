import unittest
import weather
import weather_test_data

class TestReports(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_report(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {"total" : 2, "dry" : 1, "rainy" : 1, "ratio" : 0.5})
    def test_missing_days(self):
        report = weather.create_report(weather_test_data.missing_days)
        self.assertEqual(report, {"total" : 1, "dry" : 1, "rainy" : 0, "ratio" : 0.0})
    def test_missing_precipitations(self):
    def test_missing_time_array(self):
    def test_missing_precipitation_array(self):
    def test_missing_daily_dict(self):
class TestCreateRainfallData(unittest.TestCase):

    def test_sunny_day(self):
        rainfall = weather.create_rainfall_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(rainfall, 0.7)
    def test_missing_days(self):
    def test_missing_precipitations(self):
    def test_missing_time_array(self):
    def test_missing_precipitation_array(self):
    def test_missing_daily_dict(self):
class TestCreateWeatherCodesData(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_weather_codes_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {3: 1, 61: 1})
    def test_missing_days(self):
    def test_missing_codes(self):
    def test_missing_time_array(self):
    def test_missing_codes_array(self):
    def test_missing_daily_dict(self):

if __name__ == '__main__':
    unittest.main()