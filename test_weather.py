import unittest
import weather
import weather_test_data

class TestReports(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_report(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {"total" : 2, "dry" : 1, "rainy" : 1, "ratio" : 0.5})

class TestCreateRainfallData(unittest.TestCase):

    def test_sunny_day(self):
        rainfall = weather.create_rainfall_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(rainfall, 0.7)

class TestCreateWeatherCodesData(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_weather_codes_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {3: 1, 61: 1})

if __name__ == '__main__':
    unittest.main()