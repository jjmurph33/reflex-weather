import urllib,json
import datetime
import reflex as rx

zipdata = dict() # {zip: (lat,lon)}

class State(rx.State):
    zipcode: str
    time_updated: str
    raw_data: str
    forecast_url: str
    forecast: list[dict] # list of forecast periods [today, tonight, tomorrow, ...]
    loaded: bool

    def lookup_button_handler(self,form_data: dict[str, str]):
        new_zip = form_data.get('zipcode')
        if new_zip:
            self.zipcode = new_zip
        self._check_weather()

    def on_load(self):
        self.zipcode = '02212' # boston
        self.loaded = False

    def _get_location(self):
        lat = lon = None
        location = zipdata.get(self.zipcode)
        if location:
            lat = location[0]
            lon = location[1]
        else:
            lat = 42.1979
            lon = -71.0604
        return (lat,lon)

    def _check_weather(self):
        (lat,lon) = self._get_location()
        url = f'https://api.weather.gov/points/{lat},{lon}'

        #print(url)

        weather_request = urllib.request.urlopen(url)
        weather_content = json.loads(weather_request.read())
        self.forecast_url = weather_content['properties']['forecast']

        #print(f'Checking weather at {self.forecast_url}')

        forecast_request = urllib.request.urlopen(self.forecast_url)
        forecast_content = json.loads(forecast_request.read())

        #time_now = datetime.datetime.now().astimezone(datetime.timezone.utc)

        self.time_updated = datetime.datetime.fromisoformat(forecast_content['properties']['updated'])

        #self.time_diff = time_now - self.time_updated

        periods = forecast_content['properties']['periods']

        self.forecast = list()
        for i in range(3):
            self.forecast.append(periods[i])

        data = ''.join(str(periods))
        #print(data)
        self.raw_data = data

        self.loaded = True

