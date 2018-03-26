import magicseaweed
#from magicseaweed import MagicSeaWeed
import json

key = "f34cda31d67756ac87f25854c081e57d"
secret = "53311f6e50773310e6bacb6b8e377f6c"
ponce_id = 348
bethune_id= 371
lat = "28.869533"
lon = "-81.296013"


#msw_ponce = MagicSeaWeed(key, ponce_id, None, 'us')
#msw_ponce = MagicSeaWeed(key, ponce_id, ['timestamp','swell.*','charts.*'], 'us')
#print(msw_ponce.get_forecasts(num_days=3)[0].get_weather_icon())
#print(len(msw_ponce.get_forecasts()))

#print(json.dumps(msw_ponce.get_forecast(), indent=2))
#msw_bethune = MagicSeaWeed(key, msw_ponce, None)



forecast = magicseaweed.load_forecast(key, ponce_id, None, None, None)
current = forecast.current()
print(current.summary)

next = forecast.next()
print(next.summary)

#six_hour = forecast.six_hour()
#for hour in six_hour.data:
#    print(hour.summary)

sunrise = forecast.sunrise(lat, lon)
print(sunrise.summary)
#print(sunrise.local_time)
