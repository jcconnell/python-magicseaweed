python-magicseaweed
==============================================================================================================================================================================================

Provides basic API to [Magic Seaweed](https://magicseaweed.com/developer/api).

## Install

`pip install magicseaweed`

## Usage

```python
from magicseaweed import MagicSeaWeed

msw = MagicSeaWeed("your-api-key", spot_id)
```

Example Response:
```jscon
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

## Development

Pull requests welcome.

## Disclaimer

Not affiliated with magicseaweed.com. Use at your own risk.

## TODO:
- Everything

## NOTES:

The Magic Seaweed API is currently in beta. To obtain an API key, please follow the instructions available here [Sign Up](https://magicseaweed.com/developer/sign-up)
- Email [general@magicseaweed.com](mailto:general@magicseaweed.com) with the following information
- Mention that you’ve read and agree our Terms and Conditions. We’ll be unable to offer access unless this is the case.
- A URL for your application if web based
- Your business or personal name
- A name for your application and some very basic details

## REFERENCES:
- https://magicseaweed.com/developer/forecast-api
