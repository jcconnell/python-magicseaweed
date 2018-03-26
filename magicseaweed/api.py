import requests
import threading

from magicseaweed.models import MSW_Forecast

MSW_URL = 'http://magicseaweed.com/api/{}/forecast'
HTTP_GET = 'GET'
ERROR_RESPONSE = 'error_response'
UNITS = ['us', 'uk', 'eu']
FIELD_TYPES = ['timestamp', 'localTimestamp', 'issueTimestamp', 'fadedRating',
               'solidRating', 'threeHourTimeText', 'swell.minBreakingHeight',
               'swell.*', 'swell.absMinBreakingHeight', 'swell.maxBreakingHeight',
               'swell.absMaxBreakingHeight', 'swell.probability', 'swell.unit',
               'swell.components[].absHeight', 'swell.components[].period',
               'swell.components[].direction', 'swell.components[].compassDirection',
               'swell.components[].isIncoming', 'wind.*', 'wind.speed', 'wind.direction',
               'wind.compassDirection', 'wind.chill', 'wind.gusts', 'wind.unit',
               'condition.*', 'condition.temperature', 'condition.weather', 'condition.pressure',
               'condition.unitPressure', 'condition.unit', 'charts.*', 'charts.swell',
               'charts.period', 'charts.wind', 'charts.pressure', 'charts.sst']


def _validate_unit_types(unit):
    """Validate unit types"""
    if unit not in UNITS:
        raise ValueError('Invalid unit type: {}'.format(unit))


def _validate_field_types(field_types):
    """Validate field types"""
    for field_type in field_types:
        if field_type not in FIELD_TYPES:
            raise ValueError('Invalid field type: {}'.format(field_type))


def load_forecast(api_key, spot_id, fields=None, units=None,
                  callback=None):
    """
        This function builds the request url
        API details https://magicseaweed.com/developer/forecast-api

        key:        Magic Seaweed API key
        spot_id:    The ID of a location, available from the URL when visiting the
                    corresponding spot on the Magic Seaweed website. IE '616' in
                    http://magicseaweed.com/Pipeline-Backdoor-Surf-Report/616/
        fields:     Comma separated list of fields to include in the request
                    URL. Defaults to none, which returns all information. Specifying
                    fields may reduce response time. Example:
                    fields=timestamp,wind.*,condition.temperature
        units:      A string of the preferred unit of measurement. Defaults to unit at
                    location of spot_id. eu, uk, us are available
    """

    params = {'spot_id': spot_id}
    if fields:
        _validate_field_types(fields)
        params['fields'] = ','.join(fields)
    if units:
        _validate_unit_types(unit)
        params['units'] = unit

    baseURL = requests.Request(HTTP_GET, MSW_URL.format(api_key), params=params).prepare().url
    return manual(baseURL, callback=callback)


def manual(requestURL, callback=None):
    """
        This function is used by load_msw OR by users to manually
        construct the URL for an API call.
    """

    if callback is None:
        return get_msw(requestURL)
    else:
        thread = threading.Thread(target=load_async,
                                  args=(requestURL, callback))
        thread.start()


def get_msw(requestURL):
    msw_reponse = requests.get(requestURL)
    msw_reponse.raise_for_status()

    json = msw_reponse.json()
    headers = msw_reponse.headers

    return MSW_Forecast(json, msw_reponse, headers)


def load_async(url, callback):
    callback(get_msw(url))
