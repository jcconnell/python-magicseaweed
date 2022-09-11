import os
import json
import unittest
from unittest.mock import MagicMock, patch

import magicseaweed

# randomly generated, not a real api key
TEST_API_KEY = 'Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2'
TEST_SPOT_ID = '123'
TEST_TIMESTAMP = '1662832800'
TEST_URL = 'http://testurl.com'


def load_test_fixture(filename):
    file_dir = os.path.dirname(__file__)
    fixture_path = os.path.join(
        file_dir, 'fixtures', filename)

    with open(fixture_path, 'r') as f:
        file_content = f.read()
        return json.loads(file_content)


def prepare_mock(mock_requests, status_code, fixture_filename):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = load_test_fixture(
        fixture_filename)
    mock_requests.get.return_value = mock_response


class TestHelperFunctions(unittest.TestCase):

    def test_invalid_unit(self):
        self.assertRaises(
            ValueError, magicseaweed._validate_unit_types, "invalid")

    def test_valid_units(self):
        units = ['us', 'uk', 'eu']
        for unit in units:
            magicseaweed._validate_unit_types(unit)

    def test_invalid_field(self):
        self.assertRaises(
            ValueError, magicseaweed._validate_field_types, "invalid")

    def test_valid_field(self):
        magicseaweed._validate_field_types('timestamp')

    def test_invalid_fields_string(self):
        fields = "timestamp,wind.*,invalid"
        self.assertRaises(
            ValueError, magicseaweed._validate_field_types, fields)

    def test_valid_fields_string(self):
        fields = "timestamp,wind.*,condition.temperature"
        magicseaweed._validate_field_types(fields)

    def test_forecast_transform(self):

        flattened_json = {
            'timestamp': 1662847200,
            'localTimestamp': 1662832800,
            'issueTimestamp': 1662811200,
            'fadedRating': 0,
            'solidRating': 2,
            'swell_absMinBreakingHeight': 2.65,
            'swell_absMaxBreakingHeight': 4.14,
            'swell_probability': 100,
            'swell_unit': 'ft',
            'swell_minBreakingHeight': 3,
            'swell_maxBreakingHeight': 4,
            'swell_components_combined_height': 4,
            'swell_components_combined_period': 11,
            'swell_components_combined_direction': 252.62,
            'swell_components_combined_compassDirection': 'ENE',
            'swell_components_primary_height': 3,
            'swell_components_primary_period': 11,
            'swell_components_primary_direction': 253.48,
            'swell_components_primary_compassDirection': 'ENE',
            'swell_components_secondary_height': 2.5,
            'swell_components_secondary_period': 9,
            'swell_components_secondary_direction': 225.52,
            'swell_components_secondary_compassDirection': 'NE',
            'swell_components_tertiary_height': 0.6,
            'swell_components_tertiary_period': 9,
            'swell_components_tertiary_direction': 293.08,
            'swell_components_tertiary_compassDirection': 'ESE',
            'wind_speed': 8,
            'wind_direction': 5,
            'wind_compassDirection': 'S',
            'wind_chill': 88,
            'wind_gusts': 14,
            'wind_unit': 'mph',
            'condition_pressure': 1014,
            'condition_temperature': 81,
            'condition_weather': '9',
            'condition_unitPressure': 'mb',
            'condition_unit': 'f',
            'charts_swell':
                ('https://charts-s3.msw.ms/live/wave/'
                 '2022091000/750/21-1662843600-24.gif'),
            'charts_period':
                ('https://charts-s3.msw.ms/live/wave/'
                 '2022091000/750/21-1662843600-25.gif'),
            'charts_wind':
                ('https://charts-s3.msw.ms/live/gfs/'
                 '2022091012/750/21-1662843600-4.gif'),
            'charts_pressure':
                ('https://charts-s3.msw.ms/live/gfs/'
                 '2022091012/750/21-1662843600-3.gif'),
            'charts_sst':
                'https://charts-s3.msw.ms/archive/sst/750/21-1662843600-10.gif'
        }

        transformed = magicseaweed._forecast_transform(flattened_json)

        self.assertEqual(transformed.get('air_pressure'), '1014mb')
        self.assertEqual(transformed.get('air_temp'), '81° f')
        self.assertEqual(transformed.get('stars'), '2 solid, 0 faded')
        self.assertEqual(transformed.get('begins'), 'Sat 6 PM')
        self.assertEqual(transformed.get('issued'), 'Sat 12 PM')
        self.assertEqual(transformed.get('max_breaking_height'), '4 ft')
        self.assertEqual(transformed.get(
            'abs_max_breaking_height'), '4.14 ft')
        self.assertEqual(transformed.get('min_breaking_height'), '3 ft')
        self.assertEqual(transformed.get(
            'abs_min_breaking_height'), '2.65 ft')
        self.assertEqual(transformed.get('probability'), '100%')
        self.assertEqual(transformed.get('swell_direction'), 'ENE')
        self.assertEqual(transformed.get('swell_period'), '11 seconds')
        self.assertEqual(transformed.get('wind_chill'), '88°')
        self.assertEqual(transformed.get('wind_direction'), '5° S')
        self.assertEqual(transformed.get('wind_gusts'), '14 mph')
        self.assertEqual(transformed.get('wind_speed'), '8 mph')

    def test_build_request_defaults(self):
        want = ('http://magicseaweed.com/api/Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2/'
                'forecast?spot_id=123')
        self.assertEqual(magicseaweed.build_request(
            TEST_API_KEY, TEST_SPOT_ID), want)

    def test_build_request_valid_fields(self):
        fields = "timestamp,wind.*,condition.temperature"
        want = ('http://magicseaweed.com/api/Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2/'
                'forecast?spot_id=123&fields=timestamp%2Cwind.%2A%2Ccondition.'
                'temperature')
        self.assertEqual(magicseaweed.build_request(
            TEST_API_KEY, TEST_SPOT_ID, fields=fields), want)

    def test_build_request_valid_fields_with_spaces(self):
        fields = " timestamp, wind.* "
        want = ('http://magicseaweed.com/api/Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2/'
                'forecast?spot_id=123&fields=timestamp%2Cwind.%2A')
        self.assertEqual(magicseaweed.build_request(
            TEST_API_KEY, TEST_SPOT_ID, fields=fields), want)

    def test_build_request_valid_unit(self):
        us_unit = "us"
        want = ('http://magicseaweed.com/api/Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2/'
                'forecast?spot_id=123&units=us')
        self.assertEqual(magicseaweed.build_request(TEST_API_KEY, TEST_SPOT_ID,
                                                    unit=us_unit), want)

    def test_build_request_valid_start_and_end(self):
        want = ('http://magicseaweed.com/api/Cu4do7TrIWzDXnZm3XvhX7c5Zfk0HpI2/'
                'forecast?spot_id=123&start=1662832800&end=1662832800')
        self.assertEqual(magicseaweed.build_request(
            TEST_API_KEY, TEST_SPOT_ID, start=TEST_TIMESTAMP,
            end=TEST_TIMESTAMP), want)

    @patch('magicseaweed.requests')
    def test_get_msw_success(self, mock_requests):

        prepare_mock(mock_requests, 200, 'success_response.json')

        got = magicseaweed.get_msw(TEST_URL)

        self.assertEqual(
            got.summary, '40 forecasts from Thu 12 AM to Mon 9 PM')

    @patch('magicseaweed.requests')
    def test_get_msw_error(self, mock_requests):

        prepare_mock(mock_requests, 200, 'error_response.json')

        self.assertRaises(Exception,
                          magicseaweed.get_msw, TEST_URL)


class Test_MSW_Forecast(unittest.TestCase):

    @patch('magicseaweed.requests')
    def test_MSW_Forecast_Current(self, mock_requests):
        prepare_mock(mock_requests, 200, 'success_current_response.json')

        got = magicseaweed.MSW_Forecast(TEST_API_KEY, TEST_SPOT_ID)

        want = {
            "air_pressure": "1017mb",
            "air_temp": "80° f",
            "stars": "2 solid, 0 faded",
            "begins": "Sat 9 PM",
            "issued": "Sat 6 PM",
            "max_breaking_height": "4 ft",
            "abs_max_breaking_height": "3.64 ft",
            "min_breaking_height": "2 ft",
            "abs_min_breaking_height": "2.33 ft",
            "probability": "100%",
            "swell_direction": "ENE",
            "swell_period": "11 seconds",
            "wind_chill": "90°",
            "wind_direction": "334° SSE",
            "wind_gusts": "2 mph",
            "wind_speed": "1 mph"
        }
        self.assertEqual(got.get_current().attrs, want)


if __name__ == '__main__':
    unittest.main()
