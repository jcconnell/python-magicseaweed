python-magicseaweed
==============================================================================================================================================================================================

Provides basic API to [Magic Seaweed](https://magicseaweed.com/developer/api).

## Install

`pip install python-magicseaweed`

## Requirements

- You need an API key to use it. Check the notes section for signup info.

## Usage

###### Basic Use

No familiarity with the Magic Seaweed API is required to use this package. For reference, you can find their API documentation here: [Magic Seaweed Docs](https://magicseaweed.com/developer/forecast-api). This package provides some default API interactions based on time.

To use the wrapper:

```python
import magicseaweed

api_key = os.environ.get('MSW_API_KEY')
ponce_id = 348
bethune_id = 371

ponce_forecast = MSW_Forecast(api_key, ponce_id)
ponce_now = ponce_forecast.get_current()
print(ponce_now.attrs)

bethune_forecast = MSW_Forecast(api_key, bethune_id)
bethune_future = bethune_forecast.get_future()
print(bethune_future.summary)

for forecast in bethune_future.data:
    print(forecast.attrs)
    print(forecast.get_chart_url('swell'))
```


The ``MSW_forecast()`` class has a few optional parameters. Your API key, and a spot id are the only required parameters.

Use the ``forecast.DataBlockType()`` eg. ``current()``, ``future()``, ``all()``, ``manual()``, methods to load the data you are after.

``current()`` Returns a single forecast. All other methods return a block of forecasts.
- ``future()``
- ``all()``
- ``manual()``

The .data attributes for each DataBlock is a list of Forecast objects.

```python
ponce_future = ponce_forecast.get_future()
for forecast in ponce_future.data:
    print(forecast.summary)
```

Example API Response:
```json5
[{
timestamp: 1366902000,
localTimestamp: 1366902000,
issueTimestamp: 1366848000,
fadedRating: 0,
solidRating: 0,
swell: {
    minBreakingHeight: 1,
    absMinBreakingHeight: 1.06,
    maxBreakingHeight: 2,
    absMaxBreakingHeight: 1.66,
    unit: "ft",
    components: {
         combined: {
         height: 1.1,
         period: 14,
         direction: 93.25,
         compassDirection: "W"
    },
    primary: {
         height: 1,
         period: 7,
         direction: 83.37,
         compassDirection: "W"
    },
    secondary: {
         height: 0.4,
         period: 9,
         direction: 92.32,
         compassDirection: "W"
    },
    tertiary: {
         height: 0.3,
         period: 13,
         direction: 94.47,
         compassDirection: "W"
     }
     }
},
wind: {
     speed: 10,
     direction: 85,
     compassDirection: "W",
     chill: 15,
     gusts: 13,
     unit: "mph"
},
condition: {
     pressure: 1020,
     temperature: 18,
     unitPressure: "mb",
     unit: "c"
},
charts: {
    swell: "http://cdn.magicseaweed.com/wave/750/1-1366902000-1.gif",
    period: "http://cdn.magicseaweed.com/wave/750/1-1366902000-2.gif",
    wind: "http://cdn.magicseaweed.com/gfs/750/1-1366902000-4.gif",
    pressure: "http://cdn.magicseaweed.com/gfs/750/1-1366902000-3.gif",
    sst: "http://cdn.magicseaweed.com/sst/750/1-1366902000-10.gif"
}
}]
```

##### Advanced

----------------------------------------------------

*class* MSW_Forecast(api_key, spot_id, fields, units)
------------------------------------

This class is for interacting with the MSW API. You can use it's functions to get points or series of data for different time periods.

**Parameters**:
  * **api_key** - Your API key from https://magicseaweed.com/developer/forecast-api
  * **spot_id** - The ID of a location, available from the URL when visiting the corresponding spot on the Magic Seaweed website. IE '616' in http://magicseaweed.com/Pipeline-Backdoor-Surf-Report/616/
  * **fields** - (optional) Comma separated list of fields to include in the request URL. Defaults to none, which returns all information. Specifying fields may reduce response time. Example: ['timestamp','wind.*','condition.temperature']
  * **units** - (optional) A string of the preferred unit of measurement. Defaults to unit at location of spot_id. eu, uk, us are available

**Methods**
  * **get_current()**
        - This fucntion returns a single datapoint representing the forecast providedd by MSW if you called the API with ``start=dt.now().timestamp()`` and ``end=dt.now().timestamp()``. Returns a **ForecastDataPoint**.
  * **get_future()**
        - This fucntion returns a group of datapoints, beginning with the current forecast and each representing the forecast for a 3 hour period over a 96 hour series (4 days). Returns a **ForecastDataBlock**.
  * **get_all()**
        - This function returns the default MSW response if no time parameters are added. This is usually 5 days of forecasts in 3 hour intervals. You may receive some forecasts for expired times. Returns a **ForecastDataBlock**.
  * **get_manual(start, end)**
        - This fucntion allows requests for manually selected periods of time using the start and end parameters. Returns a **ForecastDataBlock**.
    - **start** - A local timestamp from which the forecast should being. Example: ``datetime.now().timestamp()``
    - **end** - A local timestamp from which the forecast should end. Example: ``datetime.now().timestamp()``

----------------------------------------------------


*class* ForecastDataBlock
---------------------------------------------

Contains data about a forecast over time and the HTTP response from Magicseaweed.

**Attributes**
  - **http_headers**
    - A dictionary of response headers.
  - **response**
    - The Response object returned from requests request.get() method. See https://requests.readthedocs.org/en/latest/api/#requests.Response
  - **summary**
    - A human-readable text summary of this data block.
  - **data**
    - An array of **ForecastioDataPoint** objects (see below), ordered by time.

----------------------------------------------------


*class* ForecastDataPoint
---------------------------------------------

Contains data about a forecast at a particular time and the HTTP response from Magicseaweed.

Data points have many attributes, but **not all of them are always available**. Some commonly used ones are:
  - **localTimestamp**
    - The time at which the forecast begins, adjusted for the spot's timezone.
  - **swell_maxBreakingHeight**
    - A numerical value representing the height of the maxmimum wave for this forecast.

**Attributes**
  - **http_headers**
    - A dictionary of response headers.
  - **response**
    - The Response object returned from requests request.get() method. See https://requests.readthedocs.org/en/latest/api/#requests.Response
  - **summary**
	- A human-readable text summary of this data point.
  - **d**
	- A dictionary of the JSON response from the MSW API.
  - **f_d**
	- A flattened dictionary of the the JSON response from the MSW API. Keys are compressed using the '_' character.
  - **attrs**
	- A human-readable form of the attributes from this forecast.

**Methods**
  - **get_swell_url()**
    - This fucntion returns a URL formatted for the swell direction of this forecast.
  - **get_wind_url()**
    - This fucntion returns a URL formatted for wind swell direction of this forecast.

For a full list of ForecastDataPoint attributes and attribute descriptions, take a look at the table from the Magicseaweed [documentation](https://magicseaweed.com/developer/forecast-api). NOTE: While the MSW API accepts fields in dot.notation, use snake_case to access these attributes in a ForecastDataPoint.

----------------------------------------------------


## Development

Pull requests welcome.

## Disclaimer

Not affiliated with magicseaweed.com. Use at your own risk.

## TODO:
- Compile chart into animated GIFs for the ForecastDataBlocks

## NOTES:

The Magic Seaweed API is currently in beta. To obtain an API key, please follow the instructions available here [Sign Up](https://magicseaweed.com/developer/sign-up)
- Email [general@magicseaweed.com](mailto:general@magicseaweed.com) with the following information
- Mention that you’ve read and agree our Terms and Conditions. We’ll be unable to offer access unless this is the case.
- A URL for your application if web based
- Your business or personal name
- A name for your application and some very basic details

## REFERENCES:
- https://magicseaweed.com/developer/forecast-api
