from magicseaweed.utils import PropertyUnavailable
import datetime
import ephem
import requests

DEBUG = False
CDN_URL = "http://cdnimages.magicseaweed.com/30x30/{}.png"
HTTP_GET = 'GET'
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


class MSW_Forecast():

    def __init__(self, data, response, headers):
        self.response = response
        self.http_headers = headers
        self.json = data

    def update(self):
        r = requests.get(self.response.url)
        self.json = r.json()
        self.response = r

    def current(self):
        return self._msw_data('current')

    def next(self):
        return self._msw_data('next')

    def six_hour(self):
        return self._msw_data('six_hour')

    def daily(self, num_days):
        return self._msw_data('daily')

    def next_day(self): # Returns data block of next 24 hours (next 8 data points)
        return self._msw_data('next_day')

    def sunrise(self, lat, lon):
        here = ephem.Observer()
        here.lat, here.lon, here.date = lat, lon, datetime.datetime.utcnow()
        utc_sunrise = here.next_rising(ephem.Sun())
        if DEBUG:
            sunrise = ephem.localtime(utc_sunrise)
        abs_td = datetime.timedelta.max
        for i in self._msw_data('all').data:
            if DEBUG:
                print("i.timestamp: " + str(datetime.datetime.utcfromtimestamp(i.timestamp)))
            this_td = utc_sunrise.datetime() - datetime.datetime.utcfromtimestamp(i.timestamp)
            if this_td >= datetime.timedelta(milliseconds=1) and this_td < abs_td:
                abs_td = this_td
            else:
                if DEBUG:
                    print("utc_sunrise: " + str(utc_sunrise.datetime()))
                    print("sunrise: " + str(sunrise))
                    print("this i.timestamp: " + str(datetime.datetime.utcfromtimestamp(i.timestamp)))
                    print("i.localtimestamp: " + str(datetime.datetime.utcfromtimestamp(i.localTimestamp)))
                return i

    def sunset(self, lat, lon):
        here = ephem.Observer()
        here.lat, here.lon, here.date = lat, lon, datetime.datetime.utcnow()
        utc_sunset = here.next_setting(ephem.Sun())
        if DEBUG:
            sunset = ephem.localtime(utc_sunset)
        abs_td = datetime.timedelta.max
        for i in self._msw_data('all').data:
            if DEBUG:
                print("i.timestamp: " + str(datetime.datetime.utcfromtimestamp(i.timestamp)))
            this_td = utc_sunset.datetime() - datetime.datetime.utcfromtimestamp(i.timestamp)
            if this_td >= datetime.timedelta(milliseconds=1) and this_td < abs_td:
                abs_td = this_td
            else:
                if DEBUG:
                    print("utc_sunset: " + str(utc_sunset.datetime()))
                    print("sunset: " + str(sunset))
                    print("this i.timestamp: " + str(datetime.datetime.utcfromtimestamp(i.timestamp)))
                    print("i.localtimestamp: " + str(datetime.datetime.utcfromtimestamp(i.localTimestamp)))
                return i

    def all(self):
        return self._msw_data('all')

    def _msw_data(self, key):
        keys = ['current', 'next', 'six_hour', 'daily', 'next_day', 'all', 'sunrise', 'sunset']
        msw_key = FIELD_TYPES
        try:
            self.json = requests.get(self.response.url).json()
            if key == 'current':
                return ForecastDataPoint(self.json[0], 'Current')
            if key == 'next':
                return ForecastDataPoint(self.json[1], 'Next')
            if key == 'next_day':
                return ForecastDataPoint(self.json[7])
            if key == 'six_hour':
                return ForecastDataBlock(self.json[0::2], 'Six Hour') # 2 * 3hr = 6hrs
            if key == 'daily':
                return ForecastDataBlock(self.json[0::8], 'Daily') # 8 * 3hr = 24hrs
            else:
                return ForecastDataBlock(self.json)
        except:
            if key == 'current':
                return ForecastDataPoint()
            else:
                return ForecastDataBlock()


class ForecastDataBlock():

    def __init__(self, d=None, name="All"):
        d = d or {}
        if name == 'All':
            self.summary = 'All forecasts'
        else:
            self.summary = "{} forecast".format(name)

        self.data = [ForecastDataPoint(datapoint)
                     for datapoint in d]

    def __unicode__(self):
        return '<ForecastDataBlock instance: ' \
               '%s with %d ForecastDataPoints>' % (self.summary,
                                                     len(self.data),)


class ForecastDataPoint():

    def __init__(self, d={}, type=None):
        self.d = d
        self.type = type

        try: # local time this data point is expected to occur
            self.local_time = datetime.datetime.utcfromtimestamp(int(d['localTimestamp']))
            self.local_u_time = d['localTimestamp']
        except:
            pass

        try: # Try to set the issue time of this data point
            self.issue_time = datetime.datetime.utcfromtimestamp(int(d['issueTimestamp']))
            self.issue_u_time = d['issueTimestamp']
        except:
            pass

        try:
            self.summary = self._friendly_forecast()
        except:
            pass
        try:
            self.keys = self._get_keys()
        except:
            pass
        try:
            self.rating = self._get_rating()
        except:
            pass

    def __getattr__(self, name):
        try:
            return self.d[name]
        except KeyError:
            raise PropertyUnavailable(
                "Property '{}' is not valid"
                " or is not available for this forecast".format(name)
            )

    def __unicode__(self):
        return '<ForecastDataPoint instance: ' \
               '%s at %s>' % (self.summary, self.local_time,)

    def _get_keys(self):
        try:
            return self.d.keys()
        except KeyError:
            raise KeysUnavailable(
                "No keys in this forecast" )

    def _friendly_forecast(self):
        description = "{}% chance of waves breaking " \
                "between {}{} and {}{} high."
        swell = self.d.get('swell')
        return description.format(swell.get('probability'),
                swell.get('minBreakingHeight'),
                swell.get('unit'),
                swell.get('maxBreakingHeight'),
                swell.get('unit'))

    def _get_rating(self):
        """Return array of URLs for star rating."""
        rating = []
        for i in range(0,self.d.get('solidRating')):
            rating.append(STAR_FILLED_URL)
        for i in range(0,self.d.get('fadedRating')):
            rating.append(STAR_EMPTY_URL)
        return rating

    def _get_rating_num(self):
        """Return decimal representation of star rating."""
        rating = self.d.get('solidRating') + (self.d.get('fadedRating') * 0.1)
        return rating

    def _get_weather_icon(self):
        """Weather icon number. Absolute URL to weather icons."""
        icon_num = self.d.get('condition').get('weather')
        return requests.Request(HTTP_GET, CDN_URL.format(icon_num)).prepare().url


