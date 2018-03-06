"""Magic Seaweed API."""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import requests
import datetime


MSW_URL = 'http://magicseaweed.com/api/{}/forecast'
HOMEPAGE_URL = 'https://magicseaweed.com/'
CDN_URL = "http://cdnimages.magicseaweed.com/30x30/{}.png"
USER_AGENT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
ATTRIBUTION = 'Information provided by magicseaweed.com'
HTTP_GET = 'GET'
FIELD_TYPES = ['timestamp', 'localTimestamp', 'issueTimestamp', 'fadedRating', 'solidRating', 'threeHourTimeText',
        'swell.minBreakingHeight', 'swell.absMinBreakingHeight', 'swell.maxBreakingHeight', 'swell.absMaxBreakingHeight',
        'swell.probability', 'swell.unit', 'swell.components[].absHeight', 'swell.components[].period', 'swell.components[].direction',
        'swell.components[].compassDirection', 'swell.components[].isIncoming', 'wind.speed', 'wind.direction', 'wind.compassDirection',
        'wind.chill', 'wind.gusts', 'wind.unit', 'condition.temperature', 'condition.weather', 'condition.pressure', 'condition.unitPressure',
        'condition.unit', 'charts.swell', 'charts.period', 'charts.wind', 'charts.pressure', 'charts.sst']


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


def _incident_in_types(incident, incident_types):
    """Validate incident type is attribute of incident types"""
    if incident.get('type') in incident_types:
        return True
    return False


class MagicSeaWeed():
    """Magic Seaweed API wrapper."""

    def __init__(self, api_key, spot_id, fields):
        self.api_key = api_key
        self.spot_id = spot_id # int
        self.fields = ','.join(fields) # comma seperate list: fields=timestamp,wind.*,condition.temperature
        self.headers = {
            'User-Agent': USER_AGENT
        }

    def _get_params(self):
        return {
            'spot_id': self.spot_id,
            'fields': self.fields
        }

    def get_weather_icon(selfi, icon_num):
        """Weather icon number. Absolute URL to weather icons."""
        # Example: http://cdnimages.magicseaweed.com/30×30/{{ICON NUMBER}}.png.
        return requests.Request(HTTP_GET, CDN_URL.format(icon_num)).prepare().url

    def get_chart_url(self, chart_type):
        """Get URL for chart type of this instantiation."""
        return requests.Request(HTTP_GET, DASHBOARD_URL).prepare().url



    def get_incidents(self):
        """Get incidents."""
        resp = requests.get(CRIME_URL, params=self._get_params(), headers=self.headers)
        incidents = []  # type: List[Dict[str, str]]
        data = resp.json()
        if ATTR_CRIMES not in data:
            return incidents
        for incident in data.get(ATTR_CRIMES):
            if _validate_incident_date_range(incident, self.days):
                if _incident_in_types(incident, self.incident_types):
                    incidents.append(_incident_transform(incident))
        return incidents
