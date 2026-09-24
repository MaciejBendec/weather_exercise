import unittest
import weather
import weather_test_data
import tempfile
import json
from unittest.mock import patch
from requests.exceptions import HTTPError,Timeout, RequestException
import pathlib

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

    def test_invalid_dateformat(self):
        report = weather.create_report(weather_test_data.invalid_dateformat)
        self.assertEqual(report, {"total" : 1, "dry" : 1, "rainy" : 0, "ratio" : 0.0})

    def test_invalid_precipitation(self):
        report = weather.create_report(weather_test_data.invalid_precipitation)
        self.assertEqual(report, {"total" : 1, "dry" : 1, "rainy" : 0, "ratio" : 0.0})

    def test_negative_precipitation(self):
        report = weather.create_report(weather_test_data.negative_precipitation)
        self.assertEqual(report, {"total" : 1, "dry" : 1, "rainy" : 0, "ratio" : 0.0})
        
    def test_divide_by_zero_precipitation(self):
        report = weather.create_report(weather_test_data.divide_by_zero_precipitation)
        self.assertEqual(report, {"total" : 0, "dry" : 0, "rainy" : 0, "ratio" : 0})
        
    
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

    def test_invalid_dateformat(self):
        rainfall = weather.create_rainfall_data(weather_test_data.invalid_dateformat)
        self.assertEqual(rainfall, 0.0)

    def test_invalid_precipitation(self):
        rainfall = weather.create_rainfall_data(weather_test_data.invalid_precipitation)
        self.assertEqual(rainfall, 0.0)

    def test_negative_precipitation(self):
        rainfall = weather.create_rainfall_data(weather_test_data.negative_precipitation)
        self.assertEqual(rainfall, 0.0)
        
    def test_divide_by_zero_precipitation(self):
        rainfall = weather.create_rainfall_data(weather_test_data.divide_by_zero_precipitation)
        self.assertEqual(rainfall, 0.0)


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

    def test_invalid_dateformat(self):
        report = weather.create_weather_codes_data(weather_test_data.invalid_dateformat)
        self.assertEqual(report, {3: 1})

class TestGetApiData(unittest.TestCase):
    def test_correct_response(self):
        """
            Mock the requests.get and check if the data is correctly saved to cache file
        """
        with patch('weather.requests.get') as patched_get:
            patched_get.return_value.status_code = 200
            patched_get.return_value.json.return_value = weather_test_data.sunny_day_scenario
            with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                weather.get_api_data(temp_json.name)
                data = json.load(temp_json)
                self.assertEqual(data, weather_test_data.sunny_day_scenario)

    def test_single_timeout(self):
        """
            Mock the requests.get and check if the data is correctly saved to cache file
            Single timeout should not interrupt the flow
        """
        with patch('weather.requests.get') as patched_get:
            patched_get.side_effect = [Timeout, unittest.mock.DEFAULT]
            patched_get.return_value.status_code = 200
            patched_get.return_value.json.return_value = weather_test_data.sunny_day_scenario
            with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                weather.get_api_data(temp_json.name)
                data = json.load(temp_json)
                self.assertEqual(data, weather_test_data.sunny_day_scenario)

    def test_two_timeouts(self):
        """
            Check timeout handling
        """
        with self.assertRaises(Timeout):
            with patch('weather.requests.get') as patched_get:
                patched_get.side_effect = Timeout
                with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                    weather.get_api_data(temp_json.name)

    def test_non_200_return_code(self):
        """
            Non-200 return code should cause HTTPError
        """
        with self.assertRaises(HTTPError):
            with patch('weather.requests.get') as patched_get:
                patched_get.return_value.status_code = 404
                with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                    weather.get_api_data(temp_json.name)

class TestGetDataFromCache(unittest.TestCase):
    def test_valid_json(self):
        with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
            json.dump(weather_test_data.sunny_day_scenario, temp_json)
            temp_json.flush()
            data = weather.get_data_from_cache(temp_json.name)
            self.assertEqual(data, weather_test_data.sunny_day_scenario)

    def test_missing_daily_dict(self):
        with self.assertRaises(ValueError):
            with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                json.dump(weather_test_data.missing_daily_dict, temp_json)
                temp_json.flush()
                weather.get_data_from_cache(temp_json.name)

    def test_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
                temp_json.write("I'm not a Json")
                temp_json.flush()
                weather.get_data_from_cache(temp_json.name)

class TestHandleCache(unittest.TestCase):
    """
        Focus on handling parameters - internals were tested before
        Test all 4 combinations of cache existing and refresh setting
        as it is easy to write the condition in a wrong way (as I did at first)
    """
    def setUp(self):
        patcher_gdfc = patch("weather.get_data_from_cache")
        self.mock_get_data_from_cache = patcher_gdfc.start()
        self.addCleanup(patcher_gdfc.stop)
        patcher_gad = patch("weather.get_api_data")
        self.mock_get_api_data = patcher_gad.start()
        self.addCleanup(patcher_gad.stop)

    def test_cache_exists_refresh_false(self):
        #only scenario that reuses the cache
        with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
            weather.handle_cache(pathlib.Path(temp_json.name), False)
            self.mock_get_data_from_cache.assert_called_once()
            self.mock_get_api_data.assert_not_called()


    def test_cache_exists_refresh_true(self):
        with tempfile.NamedTemporaryFile(mode='w+') as temp_json:
            weather.handle_cache(pathlib.Path(temp_json.name), True)
            self.mock_get_data_from_cache.assert_called_once()
            self.mock_get_api_data.assert_called_once()

    def test_cache_does_not_exists_refresh_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = pathlib.Path(temp_dir) / "cache.json"
            weather.handle_cache(cache_file, False)
            self.mock_get_data_from_cache.assert_called_once()
            self.mock_get_api_data.assert_called_once()

    def test_cache_does_not_exists_refresh_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = pathlib.Path(temp_dir) / "cache.json"
            weather.handle_cache(cache_file, True)
            self.mock_get_data_from_cache.assert_called_once()
            self.mock_get_api_data.assert_called_once()

if __name__ == '__main__':
    unittest.main()
