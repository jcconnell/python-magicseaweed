"""Magic Seaweed API."""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import requests
import datetime
import imageio
import os

MSW_URL = 'http://magicseaweed.com/api/{}/forecast'
HOMEPAGE_URL = 'https://magicseaweed.com/'
CDN_URL = "http://cdnimages.magicseaweed.com/30x30/{}.png"
STAR_FILLED_URL = "http://cdnimages.magicseaweed.com/star_filled.png"
STAR_EMPTY_URL = "http://cdnimages.magicseaweed.com/star_empty.png"
USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
ATTRIBUTION = 'Information provided by magicseaweed.com'
HTTP_GET = 'GET'
SEPARATOR = ','
FORECASTS_PER_DAY = 8
MAX_DAYS = 5
ERROR_RESPONSE = 'error_response'
FIELD_TYPES = ['timestamp', 'localTimestamp', 'issueTimestamp', 'fadedRating',
               'solidRating', 'threeHourTimeText', 'swell.minBreakingHeight',
               'swell.absMinBreakingHeight', 'swell.maxBreakingHeight',
               'swell.absMaxBreakingHeight', 'swell.probability', 'swell.unit',
               'swell.components[].absHeight', 'swell.components[].period',
               'swell.components[].direction', 'condition.*', 'swell.*', 'charts.*',
               'swell.components[].compassDirection', 'charts', 'wind.*;',
               'swell.components[].isIncoming', 'wind.speed', 'wind.direction',
               'wind.compassDirection', 'wind.chill', 'wind.gusts', 'wind.unit',
               'condition.temperature', 'condition.weather', 'condition.pressure',
               'condition.unitPressure', 'condition.unit', 'charts.swell',
               'charts.period', 'charts.wind', 'charts.pressure', 'charts.sst']


def _forecast_transform(forecast):
    """Get output dict from forecast."""
    return {
        'timestamp': forecast.get_local_timestamp(),
        'rating': forecast.get_rating(),
        'swell_chart': forecast.get_chart('swell'),
        'temperature': forecast.get_temp(),
        'wind_speed': forecast.get_wind().get('speed'),
        'wind_direction': forecast.get_wind().get('direction'),
        'friendly_forecast': forecast._friendly_forecast()
    }


def _validate_field_types(field_types):
    """Validate field types"""
    for field_type in field_types:
        if field_type not in FIELD_TYPES:
            raise ValueError('Invalid field type: {}'.format(field_type))

def _get_num_days_forecasts(forecasts, days):
        """Returns one forecast per day for specified number of days."""
        if days > MAX_DAYS:
            raise ValueError('Maximum of 5 days')
        num_days = days*FORECASTS_PER_DAY
        return forecasts[0:num_days:FORECASTS_PER_DAY]

def _chart_gif(forecast_urls, chart_type):
    """Generate GIF from charts."""
    chart_name = 'chart_{}'.format(chart_type)
    if os.path.exists(chart_name):
        os.remove(chart_name)
    with imageio.get_writer(chart_name, mode='I') as writer:
        for forecast_url in forecast_urls:
            image = imageio.imread(requests.get(forecast_url).content)
            writer.append_data(image)

class MSW_Forecast():
    """Single forecast."""

    def __init__(self, forecast):
        self.forecast = forecast

    def get_timestamp(self):
        """Return UTC timestamp."""
        if 'timestamp' not in self.forecast:
            raise ValueError('No timestamp in this forecast.')
        return self.forecast.get('timestamp')

    def get_local_timestamp(self):
        """Return timezone adjusted timestamp for forecast."""
        if 'localTimestamp' not in self.forecast:
            raise ValueError('No local timestamp in this forecast.')
        return self.forecast.get('localTimestamp')

    def get_issued_timestamp(self):
        """Return timestamp when forecast made."""
        if 'issueTimestamp' not in self.forecast:
            raise ValueError('No issue timestamp in this forecast.')
        return self.forecast.get('issueTimestamp')

    def get_rating(self):
        """Return array of URLs for star rating."""
        rating = []
        if 'fadedRating' not in self.forecast or 'solidRating' not in self.forecast:
            raise ValueError('No rating in this forecast')
        for i in range(0,self.forecast.get('solidRating')):
            rating.append(STAR_FILLED_URL)
        for i in range(0,self.forecast.get('fadedRating')):
            rating.append(STAR_EMPTY_URL)
        return rating

    def get_chart(self, chart_type):
        """Get URL for chart type of this forecast."""
        if 'charts' not in self.forecast:
            raise ValueError('No charts in thie forecast.')
        charts = self.forecasts.get('charts')
        if chart_type == 'swell':
            return charts.get('swell')
        if chart_type == 'period':
            return charts.get('period')
        if chart_type == 'wind':
            return charts.get('wind')
        if chart_type == 'pressure':
            return charts.get('pressure')
        if chart_type == 'sst':
            return charts.get('sst')
        else:
            raise ValueError('Invalid chart type: {}'.format(chart_type))

    def get_temp(self):
        if 'temperature' not in self.forecast:
            raise ValueError('No temp in this forecast.')
        return self.forecast.get('condition').get('temperature')

    def get_wind(self):
        if 'speed' not in self.forecast or 'direction' not in self.forecast:
            raise ValueError('No speed or direction in this forecast')
        return {
                'speed': self.forecast.get('wind').get('speed'),
                'direction': self.forecast.get('wind').get('compassDirection')
                }

    def _friendly_forecast(self):
        if 'swell' not in self.forecast:
            raise ValueError('No swell in this forecast.')
        description = "There is a {}% chance of waves breaking " \
                "between {}{} and {}{} high."
        swell = self.forecast.get('swell')
        return description.format(swell.get('probability'),
                swell.get('minBreakingHeight'),
                swell.get('unit'),
                swell.get('maxBreakingHeight'),
                swell.get('unit'))

    def get_weather_icon(self):
        """Weather icon number. Absolute URL to weather icons."""
        if 'condition' not in self.forecast or  \
            'weather' not in self.forecast['condition']:
            raise ValueError('No condition or weather icon in this forecast.')
        icon_num = self.forecast.get('condition').get('weather')
        return requests.Request(HTTP_GET, CDN_URL.format(icon_num)).prepare().url


class MagicSeaWeed():
    """Magic Seaweed API wrapper."""

    def __init__(self, api_key, spot_id, fields, units):
        self.api_key = api_key
        self.spot_id = spot_id # int
        self.units = units # eu, uk, us
        self.headers = {
            'User-Agent': USER_AGENT
        }

    def _get_params(self, fields):
        if fields:
            _validate_field_types(fields)
            joined_fields = SEPERATOR.join(fields)
            return {
                'spot_id': self.spot_id,
                'units': self.units,
                'fields': joined_fields
            }
        return {
                'spot_id': self.spot_id,
                'units': self.units
        }

    def get_forecasts(self, fields=None, num_days=None):
        """Get forecasts."""
        resp = requests.get(MSW_URL.format(self.api_key), \
                params=self._get_params(fields))
        forecasts = []  # type: List[Dict[str, str]]
        data = resp.json()
        if ERROR_RESPONSE in data:
            return forecasts
        for forecast in data:
            #forecasts.append(_forecast_transform(MSW_Forecast(forecast)))
            forecasts.append(MSW_Forecast(forecast))
        if num_days:
            return _get_num_days_forecasts(forecasts, 3)
        _chart_gif(forecasts[0].get_chart('swell'), 'Swell')
        return forecasts
