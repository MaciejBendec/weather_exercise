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
        report = weather.create_report(weather_test_data.missing_precipitations)
        self.assertEqual(report, {"total" : 1, "dry" : 0, "rainy" : 1, "ratio" : 1.0})

    def test_missing_time_array(self):
        with self.assertRaises(ValueError):
            weather.create_report(weather_test_data.missing_time_array)
    
    def test_missing_precipitation_array(self):
        with self.assertRaises(ValueError):
            weather.create_report(weather_test_data.missing_precipitation_array)
    
class TestCreateRainfallData(unittest.TestCase):

    def test_sunny_day(self):
        rainfall = weather.create_rainfall_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(rainfall, 0.7)
    
    def test_missing_days(self):
        rainfall = weather.create_rainfall_data(weather_test_data.missing_days)
        self.assertEqual(rainfall, 0.0)
    
    def test_missing_precipitations(self):
        rainfall = weather.create_rainfall_data(weather_test_data.missing_precipitations)
        self.assertEqual(rainfall, 0.7) # empty data counts as 0
    
    def test_missing_time_array(self):
        with self.assertRaises(ValueError):
            weather.create_rainfall_data(weather_test_data.missing_time_array)
    
    def test_missing_precipitation_array(self):
        with self.assertRaises(ValueError):
            weather.create_rainfall_data(weather_test_data.missing_precipitation_array)

class TestCreateWeatherCodesData(unittest.TestCase):

    def test_sunny_day(self):
        report = weather.create_weather_codes_data(weather_test_data.sunny_day_scenario)
        self.assertEqual(report, {3: 1, 61: 1})
    
    def test_missing_days(self):
        report = weather.create_weather_codes_data(weather_test_data.missing_days)
        self.assertEqual(report, {3: 1})
    
    def test_missing_codes(self):
        report = weather.create_weather_codes_data(weather_test_data.missing_codes)
        self.assertEqual(report, {61: 1, 'unknown': 1}) # weather code is missing -> unknown
    
    def test_missing_time_array(self):
        with self.assertRaises(ValueError):
            weather.create_weather_codes_data(weather_test_data.missing_time_array)
    
    def test_missing_codes_array(self):
        with self.assertRaises(ValueError):
            weather.create_weather_codes_data(weather_test_data.missing_codes_array)

if __name__ == '__main__':
    unittest.main()
