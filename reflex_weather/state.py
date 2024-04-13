import urllib,json
import datetime
import reflex as rx
from pprint import pprint

from . import location

class State(rx.State):
    zipcode: str
    time_updated: str
    forecast_url: str
    forecast: list[dict] # list of forecast periods [today, tonight, tomorrow, ...]
    loaded: bool

    def lookup_button_handler(self,form_data: dict[str, str]):
        new_zip = form_data.get('zipcode')
        if new_zip:
            self.zipcode = new_zip
        self._check_weather()

    def on_load(self):
        if not self.zipcode:
            self.zipcode = '02212' # boston
        self.loaded = False

    def _get_location(self):
        lat = lon = None
        location_data = location.zipdata.get(self.zipcode)
        if location_data:
            (lat,lon) = location_data
        else:
            lat = 42.3584  # default to
            lon = -71.0598 # boston
        return (lat,lon)

    def _check_weather(self):
        (lat,lon) = self._get_location()
        location_url = f'https://api.weather.gov/points/{lat},{lon}'

        # TODO: add logging and error checking

        #print(location_url)
        #print('location cache:')
        #pprint(location.url_cache)

        # the location url is used to get the forecast url
        # this shouldn't change so we cache the results indefinitely
        weather_content = location.url_cache.get(location_url)
        if not weather_content:
            weather_request = urllib.request.urlopen(location_url)
            weather_content = json.loads(weather_request.read())
            location.url_cache[location_url] = weather_content

        self.forecast_url = weather_content['properties']['forecast']

        #print(f'Checking weather at {self.forecast_url}')

        forecast_request = urllib.request.urlopen(self.forecast_url)
        forecast_content = json.loads(forecast_request.read())
        # TODO: cache the forecast_content

        #time_now = datetime.datetime.now().astimezone(datetime.timezone.utc)

        self.time_updated = datetime.datetime.fromisoformat(forecast_content['properties']['updated'])

        #self.time_diff = time_now - self.time_updated

        periods = forecast_content['properties']['periods']
        self.forecast = list(periods)
        self.loaded = True

