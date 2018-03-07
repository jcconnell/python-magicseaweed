"""Magic Seaweed API."""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import requests
import datetime


MSW_URL = 'http://magicseaweed.com/api/{}/forecast'
HOMEPAGE_URL = 'https://magicseaweed.com/'
CDN_URL = "http://cdnimages.magicseaweed.com/30x30/{}.png"
STAR_FILLED_URL = "http://cdnimages.magicseaweed.com/star_filled.png"
STAR_EMPTY_URL = "http://cdnimages.magicseaweed.com/star_empty.png"
USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
ATTRIBUTION = 'Information provided by magicseaweed.com'
HTTP_GET = 'GET'
ERROR_RESPONSE = 'error_response'
FIELD_TYPES = ['timestamp', 'localTimestamp', 'issueTimestamp', 'fadedRating',
               'solidRating', 'threeHourTimeText', 'swell.minBreakingHeight',
               'swell.absMinBreakingHeight', 'swell.maxBreakingHeight',
               'swell.absMaxBreakingHeight', 'swell.probability', 'swell.unit',
               'swell.components[].absHeight', 'swell.components[].period',
               'swell.components[].direction', 'swell.components[].compassDirection',
               'swell.components[].isIncoming', 'wind.speed', 'wind.direction',
               'wind.compassDirection', 'wind.chill', 'wind.gusts', 'wind.unit',
               'condition.temperature', 'condition.weather', 'condition.pressure',
               'condition.unitPressure', 'condition.unit', 'charts.swell',
               'charts.period', 'charts.wind', 'charts.pressure', 'charts.sst']


def _validate_incident_date_range(incident, numdays):
    """Returns true if incident is within date range"""
    try:
        datetime_object = datetime.datetime.strptime(incident.get('date'), '%m/%d/%y %I:%M %p')
    except ValueError:
        raise ValueError("Incorrect date format, should be MM/DD/YY HH:MM AM/PM")
    timedelta = datetime.timedelta(days=numdays)
    today = datetime.datetime.now()
    if today - datetime_object <= timedelta:
        return True
    return False


def _incident_transform(incident):
    """Get output dict from incident."""
    return {
        'id': incident.get('cdid'),
        'type': incident.get('type'),
        'timestamp': incident.get('date'),
        'lat': incident.get('lat'),
        'lon': incident.get('lon'),
        'location': incident.get('address'),
        'link': incident.get('link')
    }


def _validate_field_types(field_types):
    """Validate field types"""
    for field_type in field_types:
        if field_type not in FIELD_TYPES:
            raise ValueError('Invalid field type: {}'.format(field_type))


class MSW_Forecast():
    """Single forecast."""

    def __init__(self, forecast):
        self.forecast = forecast

    def get_timestamp(self):
        """Return UTC timestamp."""
        if 'timestamp' not in self.forecast:
            raise ValueError('No timestamp in this forecast.')
        return self.forecast['timestamp']

    def get_local_timestamp(self):
        """Return timezone adjusted timestamp for forecast."""
        if 'localTimestamp' not in self.forecast:
            raise ValueError('No local timestamp in this forecast.')
        return self.forecast['localTimestamp']

    def get_issued_timestamp(self):
        """Return timestamp when forecast made."""
        if 'issueTimestamp' not in self.forecast:
            raise ValueError('No issue timestamp in this forecast.')
        return self.forecast['issueTimestamp']

    def get_rating(self):
        """Return array of URLs for star rating."""
        rating = []
        if 'rating' not in self.forecast:
            raise ValueError('No rating in this forecast')
        for i in range(0,self.forecast['solidRating']):
            rating.append(STAR_FILLED_URL)
        for i in range(0,self.forecast['fadedRating']):
            rating.append(STAR_EMPTY_URL)
        return rating

    def get_chart(self, chart_type):
        """Get URL for chart type of this forecast."""
        if chart_type == 'swell':
            return self.forecast['charts']['swell']
        if chart_type == 'period':
            return self.forecast['charts']['period']
        if chart_type == 'wind':
            return self.forecast['charts']['wind']
        if chart_type == 'pressure':
            return self.forecast['charts']['pressure']
        if chart_type == 'sst':
            return self.forecast['charts']['sst']
        else:
            raise ValueError('Invalid chart type: {}'.format(chart_type))

    def get_temp(self):
        return self.forecast['condition']['temperature']

    def get_wind(self):
        return {
                'speed': self.forecast['wind']['speed'],
                'direction': self.forecast['wind']['compassDirection']
                }

    def _friendly_forecast(self):
        description = "There is a {}% chance of waves breaking " \
                "between {}{} and {}{} high."
        return description.format(self.forecast['swell']['probability'],
                self.forecast['swell']['minBreakingHeight'],
                self.forecast['swell']['unit'],
                self.forecast['swell']['maxBreakingHeight'],
                self.forecast['swell']['unit'])


class MagicSeaWeed():
    """Magic Seaweed API wrapper."""

    def __init__(self, api_key, spot_id, fields, units):
        self.api_key = api_key
        self.spot_id = spot_id # int
        self.units = units # eu, uk, us
        self.headers = {
            'User-Agent': USER_AGENT
        }
        self.fields = None
        if fields:
            _validate_field_types(fields)
            self.fields = ','.join(fields) # comma separated list: fields=timestamp,wind.*,condition.temperature


    def _get_params(self):
        if self.fields:
            return {
                'spot_id': self.spot_id,
                'units': self.units,
                'fields': self.fields
            }
        return {
                'spot_id': self.spot_id,
                'units': self.units
        }

    def get_weather_icon(self, icon_num):
        """Weather icon number. Absolute URL to weather icons."""
        return requests.Request(HTTP_GET, CDN_URL.format(icon_num)).prepare().url

    def get_forecasts(self):
        """Get forecast."""
        resp = requests.get(MSW_URL.format(self.api_key), params=self._get_params())  #, headers=self.headers)
        forecasts = []  # type: List[Dict[str, str]]
        images = []
        data = resp.json()
        if ERROR_RESPONSE in data:
            return forecasts
        for forecast in data:
            _forecast = MSW_Forecast(forecast) 
            forecasts.append(_forecast)
        return forecasts[(len(forecasts)-1)]._friendly_forecast()
