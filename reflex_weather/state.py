import urllib,json
import datetime
import reflex as rx

from . import location

class State(rx.State):
    zipcode: str = rx.LocalStorage(name='zipcode') # LocalStorage saves zipcode in browser
    time_updated: str
    forecast_url: str
    forecast: list[dict] # list of forecast periods [today, tonight, tomorrow, ...]
    loaded: bool # True when the forecast is fully loaded
    error: bool # True if there were any errors during loading

    def lookup_button_handler(self,form_data: dict[str, str]):
        new_zip = form_data.get('zipcode')
        if new_zip:
            self.zipcode = new_zip
        self._check_weather()

    def on_load(self):
        if not self.zipcode:
            self.zipcode = '02212' # boston
        self.error = False
        self.loaded = False

    def _get_location(self):
        # just US zip codes for now, going to expand this later
        lat = lon = None
        (lat,lon) = location.zipdata.get(self.zipcode)
        return (lat,lon)

    def _check_weather(self):
        # the loaded and error flags are used by the front end to know what to display
        self.loaded = False
        self.error = False

        try:
            (lat,lon) = self._get_location()
            if not lat or not lon:
                self.error = True
                return

            location_url = f'https://api.weather.gov/points/{lat},{lon}'

            # TODO: add logging and error checking

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
        except:
            # catch any unhandled exceptions
            # TODO: log and report them
            self.error = True

