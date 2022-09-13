import os
import pprint
import magicseaweed
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('MSW_API_KEY')
ponce_id = 348
bethune_id = 3771
pp = pprint.PrettyPrinter(indent=4)

ponce_forecast = magicseaweed.MSW_Forecast(api_key, ponce_id)
ponce_now = ponce_forecast.get_current()
print(ponce_now.attrs)

bethune_forecast = magicseaweed.MSW_Forecast(api_key, bethune_id)
bethune_future = bethune_forecast.get_future()
print(bethune_future.summary)

for forecast in bethune_future.data:
    pp.pprint(forecast.attrs)
    pp.pprint(forecast.charts_swell)
    pp.pprint(forecast.get_swell_url('combined'))
    pp.pprint(forecast.get_wind_url())
