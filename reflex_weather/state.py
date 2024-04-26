import urllib,json
import logging
from datetime import datetime
import reflex as rx

from . import location

forecast_cache = dict()
hourly_cache = dict()

class Forecast(rx.Base):
    time: str
    short: str
    detailed: str
    temperature: str



class Weather(rx.State):
    zipcode: str = rx.LocalStorage(name='zipcode')
    forecast: list[dict] # list of forecast periods [today, tonight, tomorrow, ...]
    hourly: list[Forecast] # list of hourly forecast periods
    _status = 'ready'

    def lookup_button_handler(self):
        if self.zipcode:
            self._check_weather()

    def _get_location(self):
        # returns the latitude and longitude for use by the weather api
        # just US zip codes for now, going to expand this later
        lat = lon = None
        (lat,lon) = location.zipdata.get(self.zipcode)
        return (lat,lon)

    def _check_weather(self):
        self._status = 'loading'

        try:
            (lat,lon) = self._get_location()
            if not lat or not lon:
                self.error = True
                return

            location_url = f'https://api.weather.gov/points/{lat},{lon}'
            logging.info(f'Using location url {location_url}')

            # the location url is used to get the forecast urls
            # this content shouldn't change so we cache the results indefinitely
            weather_content = location.url_cache.get(location_url)
            if not weather_content:
                weather_request = urllib.request.urlopen(location_url)
                weather_content = json.loads(weather_request.read())
                logging.info('Weather content loaded')
                location.url_cache[location_url] = weather_content
            else:
                logging.info('Weather content loaded from cache')

            self.forecast_url = weather_content['properties']['forecast']
            logging.info(f'Checking weather at {self.forecast_url}')

            forecast_content = forecast_cache.get(self.forecast_url)
            if not forecast_content:
                forecast_request = urllib.request.urlopen(self.forecast_url)
                forecast_content = json.loads(forecast_request.read())
                logging.info('Forecast data loaded')
                forecast_cache[self.forecast_url] = forecast_content
            else:
                logging.info('Forecast data loaded from cache')

            #time_now = datetime.datetime.now().astimezone(datetime.timezone.utc)
            #self.time_updated = datetime.datetime.fromisoformat(forecast_content['properties']['updated'])
            #self.time_diff = time_now - self.time_updated

            hourly_url = weather_content['properties']['forecastHourly']
            logging.info(f'Checking hourly weather at {hourly_url}')

            hourly_content = hourly_cache.get(hourly_url)
            if not hourly_content:
                hourly_request = urllib.request.urlopen(hourly_url)
                hourly_content = json.loads(hourly_request.read())
                logging.info('Hourly forecast data loaded')
                hourly_cache[self.forecast_url] = forecast_content
            else:
                logging.info('Hourly forecast data loaded from cache')

            self.forecast = list(forecast_content['properties']['periods'])

            hourly_periods = list()
            count = 0
            for period in hourly_content['properties']['periods']:
                dt = datetime.fromisoformat(period['startTime'])
                f = Forecast(time=dt.strftime('%-I%p'),
                             short=period['shortForecast'],
                             detailed=period['detailedForecast'],
                             temperature = period['temperature'],
                             )
                hourly_periods.append(f)
                count += 1
                if count >= 12: break # only load the first 12 hours
            self.hourly = hourly_periods


            self._status = 'loaded'
        except Exception as e:
            logging.error(e)
            self._status = 'error'

    @rx.var
    def is_loading(self) -> bool:
        return self._status == 'loading'

    @rx.var
    def is_loaded(self) -> bool:
        return self._status == 'loaded'

    @rx.var
    def is_error(self) -> bool:
        return self._status == 'error'


