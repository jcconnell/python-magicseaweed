from ast import Str
import requests
from PIL import Image
from enum import Enum
from datetime import timedelta
from flatten_json import flatten
from datetime import datetime as dt


MSW_URL = 'http://magicseaweed.com/api/{}/forecast'
WEATHER_URL = 'http://cdnimages.magicseaweed.com/30x30/{}.png'
SWELL_ARROW_URL = 'http://cdnimages.magicseaweed.com/swellArrows/{}.png'
WIND_ARROW_URL = 'http://cdnimages.magicseaweed.com/newWindArrows/{}.png'
HOURS = ['12AM', '3AM', '6AM', '9AM', '12PM', '3PM', '6PM', '9PM']
HTTP_GET = 'GET'
ERROR_RESPONSE = 'error_response'
UNITS = ['us', 'uk', 'eu']
SWELL_TYPES = ['combined', 'primary', 'secondary', 'tertiary']
FIELD_TYPES = ['timestamp',
               'localTimestamp',
               'issueTimestamp',
               'fadedRating',
               'solidRating',
               'threeHourTimeText',
               'swell.minBreakingHeight',
               'swell.*',
               'swell.absMinBreakingHeight',
               'swell.maxBreakingHeight',
               'swell.absMaxBreakingHeight',
               'swell.probability',
               'swell.unit',
               'swell.components.combined.*',
               'swell.components.combined.height',
               'swell.components.combined.period',
               'swell.components.combined.direction',
               'swell.components.combined.compassDirection',
               'swell.components.primary.*',
               'swell.components.primary.height',
               'swell.components.primary.period',
               'swell.components.primary.direction',
               'swell.components.primary.compassDirection',
               'swell.components.secondary.*',
               'swell.components.secondary.height',
               'swell.components.secondary.period',
               'swell.components.secondary.direction',
               'swell.components.secondary.compassDirection',
               'swell.components.tertiary.*',
               'swell.components.tertiary.height',
               'swell.components.tertiary.period',
               'swell.components.tertiary.direction',
               'swell.components.tertiary.compassDirection',
               'wind.*',
               'wind.speed',
               'wind.direction',
               'wind.compassDirection',
               'wind.chill',
               'wind.gusts',
               'wind.unit',
               'condition.*',
               'condition.temperature',
               'condition.weather',
               'condition.pressure',
               'condition.unitPressure',
               'condition.unit',
               'charts.*',
               'charts.swell',
               'charts.period',
               'charts.wind',
               'charts.pressure',
               'charts.sst'
               ]


class Chart_type(Enum):
    SWELL = "swell"
    PERIOD = "period"
    WIND = "wind"
    PRESSURE = "pressure"
    SST = "sst"


def _validate_unit_types(unit):
    """Validate unit types"""
    if unit not in UNITS:
        raise ValueError('Invalid unit type: {}'.format(unit))


def _validate_field_types(field_types):
    """Validate field types"""
    chunked_field_types = field_types.split(',')
    for field_type in chunked_field_types:
        if field_type not in FIELD_TYPES:
            raise ValueError('Invalid field type: {}'.format(field_type))


def _flatten(d):
    """Flattens a multi-level dict, compressing keys."""
    return dict(flatten(d))


def _forecast_transform(f_d):
    """Get attribute dict from flattened forecast dict."""
    begins = f_d.get('localTimestamp', None)
    issued = f_d.get('issueTimestamp', None)
    solid_stars = f_d.get('solidRating', None)
    faded_stars = f_d.get('fadedRating', None)
    air_pressure = f_d.get('condition_pressure', None)
    unit_pressure = f_d.get('condition_unitPressure', None)
    air_temp = f_d.get('condition_temperature', None)
    unit_temp = f_d.get('condition_unit', None)
    swell_max_breaking_height = f_d.get('swell_maxBreakingHeight', None)
    swell_abs_max_breaking_height = f_d.get('swell_absMaxBreakingHeight', None)
    swell_min_breaking_height = f_d.get('swell_minBreakingHeight', None)
    swell_abs_min_breaking_height = f_d.get('swell_absMinBreakingHeight', None)
    swell_dir = f_d.get('swell_components_combined_compassDirection', None)
    swell_unit = f_d.get('swell_unit', None)
    probability = f_d.get('swell_probability', None)
    period = f_d.get('swell_components_combined_period', None)
    wind_chill = f_d.get('wind_chill', None)
    wind_gusts = f_d.get('wind_gusts', None)
    wind_direction = f_d.get('wind_compassDirection', None)
    wind_degrees = f_d.get('wind_direction', None)
    wind_speed = f_d.get('wind_speed', None)
    wind_unit = f_d.get('wind_unit', None)

    return {
        'air_pressure': "{}{}".format(air_pressure, unit_pressure),
        'air_temp': "{}° {}".format(air_temp, unit_temp),
        'stars': "{} solid, {} faded".format(solid_stars, faded_stars),
        'begins': dt.utcfromtimestamp(begins).strftime("%a %-I %p"),
        'issued': dt.utcfromtimestamp(issued).strftime("%a %-I %p"),
        'max_breaking_height': "{} {}".format(
            swell_max_breaking_height, swell_unit),
        'abs_max_breaking_height': "{} {}".format(
            swell_abs_max_breaking_height, swell_unit),
        'min_breaking_height': "{} {}".format(
            swell_min_breaking_height, swell_unit),
        'abs_min_breaking_height': "{} {}".format(
            swell_abs_min_breaking_height, swell_unit),
        'probability': "{}%".format(probability),
        'swell_direction': "{}".format(swell_dir),
        'swell_period': "{} seconds".format(period),
        'wind_chill': "{}°".format(wind_chill),
        'wind_direction': "{}° {}".format(wind_degrees, wind_direction),
        'wind_gusts': "{} {}".format(wind_gusts, wind_unit),
        'wind_speed': "{} {}".format(wind_speed, wind_unit),
    }


def build_request(api_key, spot_id, fields=None, unit=None,
                  start=None, end=None):
    """
        This function builds the request url
        API details https://magicseaweed.com/developer/forecast-api

        key:        Magic Seaweed API key
        spot_id:    The ID of a location, available from the
                    URL when visiting the corresponding spot on
                    the Magic Seaweed website. IE '616' in
                    http://magicseaweed.com/Pipeline-Backdoor-Surf-Report/616/
        fields:     Comma separated list of fields to include in the request
                    URL. Defaults to none, which returns all information.
                    Specifying fields may reduce response time. Example:
                    fields=timestamp,wind.*,condition.temperature
        units:      A string of the preferred unit of measurement. Defaults
                    to unit at location of spot_id. eu, uk, us are available
        start:      Local timestamp for the start of a desired forecast range
        end:        Local timestamp for the end of the desired forecast range
    """
    params = {'spot_id': spot_id}
    if fields:
        fields = fields.replace(" ", "")
        _validate_field_types(fields)
        params['fields'] = fields
    if unit:
        _validate_unit_types(unit)
        params['units'] = unit
    if start and end:
        params['start'] = start
        params['end'] = end

    baseURL = requests.Request(HTTP_GET, MSW_URL.format(
        api_key), params=params).prepare().url
    return baseURL


def get_msw(requestURL):
    """Get MSW API response."""
    msw_response = requests.get(requestURL)
    msw_response.raise_for_status()

    json_d = msw_response.json()
    headers = msw_response.headers

    if ERROR_RESPONSE in json_d:
        code = json_d.get(ERROR_RESPONSE).get('code')
        msg = json_d.get(ERROR_RESPONSE).get('error_msg')
        raise requests.exceptions.HTTPError(
            'API returned error code {}. {}'.format(code, msg))
    if len(json_d) == 1:
        return ForecastDataPoint(json_d[0], headers, msw_response)
    return ForecastDataBlock(json_d, headers, msw_response)


class MSW_Forecast():

    def __init__(self, api_key, spot_id, fields=None, unit=None):
        self.api_key = api_key
        self.spot_id = spot_id
        self.fields = fields
        self.unit = unit

    def get_current(self):
        """Get current forecast."""
        now = dt.now().timestamp()
        url = build_request(self.api_key, self.spot_id, self.fields,
                            self.unit, now, now)
        return get_msw(url)

    def get_future(self):
        """Get current and future forecasts."""
        now = dt.now()
        four_days = now + timedelta(hours=96)
        now = now.timestamp()
        four_days = four_days.timestamp()
        url = build_request(self.api_key, self.spot_id, self.fields,
                            self.unit, now, four_days)
        return get_msw(url)

    def get_all(self):
        """Get default forecasts, some in past."""
        url = build_request(self.api_key, self.spot_id, self.fields,
                            self.unit, None, None)
        return get_msw(url)

    def get_manual(self, start, end):
        """Get forecasts for a manually selected time period."""
        url = build_request(self.api_key, self.spot_id, self.fields,
                            self.unit, start, end)
        return get_msw(url)


class ForecastDataBlock():

    def __init__(self, d: dict | None = None, headers: dict | None = None, response: requests.Response | None = None):
        d = d or {}
        self.headers = headers
        self.response = response
        self.data = [ForecastDataPoint(datapoint)
                     for datapoint in d]
        self.summary = self._summary(self.data)

    def _summary(self, d: dict) -> str:
        try:
            num = len(d)
            start = d[0].attrs['begins']
            end = d[-1].attrs['begins']
            return "{} forecasts from {} to {}".format(num, start, end)
        except KeyError:
            return "No forecasts."

    def make_gif(self, chart_type: Chart_type) -> None:
        gif_file = '{}.gif'.format(chart_type.value)
        frames = self.load_charts(chart_type)
        frame_one = frames[0]
        frame_one.save(gif_file, format="GIF", append_images=frames,
                       save_all=True, duration=100, loop=0)

    # def get_gif_bytes(self, chart_type: Chart_type) -> bytes | None:
    #     gif_file = '{}.gif'.format(chart_type.value)
    #     frames = self.load_charts(chart_type)
    #     frame_one = frames[0]
    #     frame_one.tobytes(gif_file, format="GIF", append_images=frames,
    #                       save_all=True, duration=100, loop=0)

    def load_charts(self, chart_type: Chart_type):
        images_frames = []
        for datapoint in self.data:
            url = datapoint.get_chart_url(chart_type)
            image = Image.open(requests.get(url, stream=True).raw)
            images_frames.append(image)
        return images_frames


class ForecastDataPoint():

    def __init__(self, d={}, headers=None, response=None):
        self.d = d
        self.f_d = _flatten(d)
        self.attrs = _forecast_transform(self.f_d)
        self.headers = headers
        self.response = response
        self.summary = self._summary(d)

    def _summary(self, d):
        try:
            min_breaking_height = self.attrs['min_breaking_height']
            max_breaking_height = self.attrs['max_breaking_height']
            local_tm = self.attrs['begins']
            return "{} - {} at {}".format(min_breaking_height,
                                          max_breaking_height, local_tm)
        except KeyError:
            return None

    def __getattr__(self, name):
        dot = name.replace('_', '.')
        if dot not in FIELD_TYPES:
            raise ValueError("{} not a valid field type".format(dot))
        try:
            return self.f_d[name]
        except KeyError:
            return PropertyUnavailable(('Property {} is unavailable '
                                        'for this forecast').format(name))

    def get_swell_url(self, swell_type):
        """Get swell arrow url."""
        if swell_type not in SWELL_TYPES:
            raise ValueError('Invalid swell type: {}'.format(swell_type))
        key = "swell_components_{}_direction".format(swell_type)
        swell_direction = self.f_d.get(key)
        if swell_direction is not None:
            rounded = int(5 * round(float(swell_direction)/5))
            return SWELL_ARROW_URL.format(rounded)

    def get_wind_url(self):
        """Get wind arrow url."""
        wind_direction = self.f_d.get('wind_direction', None)
        if wind_direction is not None:
            rounded = int(5 * round(float(wind_direction)/5))
            return WIND_ARROW_URL.format(rounded)

    def get_chart_url(self, chartType):
        """Get url for the chart type."""

        if not isinstance(chartType, Chart_type):
            raise TypeError(
                'chartType must be an instance of Chart_type Enum')

        chart_type = '{}_{}'.format("charts", chartType.value)
        return self.f_d.get(chart_type, None)


class PropertyUnavailable(AttributeError):
    """Raise when an attribute is not available for a forecast."""
