from magicseaweed import MSW_Forecast
import os
import pprint

api_key = os.environ.get('MSW_API_KEY')
ponce_id = 348
bethune_id= 371
pp = pprint.PrettyPrinter(indent=4)


ponce_forecast = MSW_Forecast(api_key, ponce_id)
ponce_now = ponce_forecast.current()

print(ponce_now.attrs)

bethune_forecast = MSW_Forecast(api_key, bethune_id)
bethune_future = bethune_forecast.day()
print(bethune_future.summary)

for forecast in bethune_future.data:
    pp.pprint(forecast.attrs)
    pp.pprint(forecast.get_chart_url('swell'))
