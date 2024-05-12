import urllib,json
import logging
from datetime import datetime
import reflex as rx

from . import location

USE_MOCK_DATA = False # use the files in the testing folder instead of calling the real API

logger = logging.getLogger('weather')

forecast_cache = dict()
hourly_cache = dict()

class Forecast(rx.Base):
    time = ""
    short = ""
    detailed = ""
    temperature = ""
    icon = ""
    period_name = ""


class Weather(rx.State):
    zipcode: str = rx.LocalStorage(name='zipcode') # saved in browser
    forecast: list[Forecast] # list of forecast periods [today, tonight, tomorrow, ...]
    hourly: list[Forecast] # list of hourly forecast periods
    last_updated: str
    _status = 'ready'

    async def handle_submit(self, form: dict):
        self.zipcode = form['zip']
        logger.debug(f'zip code: {self.zipcode}')
        if self.zipcode:
            self._status = 'loading'
            yield
            url = self._get_location_url()
            if url:
                self._check_weather(url)

    def _get_location_url(self):
        # build the location url from the latitude/longitude of the zipcode
        lat = lon = None
        try:
            (lat,lon) = location.zipdata.get(self.zipcode)
        except TypeError:
            logger.error(f'Error loading location data for zipcode {self.zipcode}')
            self._status = 'error'
            return None
        return f'https://api.weather.gov/points/{lat},{lon}'

    def _load_weather(self,url):
        content = None
        if USE_MOCK_DATA:
            logger.debug(f'loading mock weather content')
            with open('testing/weather_content.json') as f:
                content = json.load(f)
        else:
            response = urllib.request.urlopen(url)
            content = json.loads(response.read())
            logger.debug('Weather content loaded')
        return content

    def _load_forecast(self,url):
        content = None
        if USE_MOCK_DATA:
            logger.debug(f'loading mock forecast content')
            with open('testing/forecast_content.json') as f:
                content = json.load(f)
        else:
            response = urllib.request.urlopen(url)
            content = json.loads(response.read())
            logger.debug('Forecast data loaded')
        time_updated = datetime.fromisoformat(content['properties']['updated'])
        time_generated = datetime.fromisoformat(content['properties']['generatedAt'])
        time_diff = time_generated - time_updated
        minutes_ago = int(time_diff.seconds / 60)
        if minutes_ago <= 1:
            self.last_updated = 'just now'
        else:
            self.last_updated = f'{minutes_ago} minutes ago'
        return content

    def _load_hourly_forecast(self,url):
        content = None
        if USE_MOCK_DATA:
            logger.debug(f'loading mock hourly content')
            with open('testing/hourly_content.json') as f:
                return json.load(f)
        else:
            response = urllib.request.urlopen(url)
            content = json.loads(response.read())
            logger.debug('Forecast data loaded')
        return content

    def _check_weather(self,url):
        try: 
            logger.info(f'Weather url: {url}')
            weather_content = self._load_weather(url)

            forecast_url = weather_content['properties']['forecast']
            logger.info(f'Forecast url {forecast_url}')
            forecast_content = self._load_forecast(forecast_url)
            self.forecast = [Forecast(short=period['shortForecast'],
                                      detailed=period['detailedForecast'],
                                      temperature = period['temperature'],
                                      icon = period['icon'],
                                      period_name = period['name'])
                            for period in forecast_content['properties']['periods']]

            hourly_url = weather_content['properties']['forecastHourly']
            logger.info(f'Hourly forecast url {hourly_url}')
            hourly_content = self._load_hourly_forecast(hourly_url)
            self.hourly = [Forecast(time=datetime.fromisoformat(period['startTime']).strftime('%A %-I%P'),
                                    short=period['shortForecast'],
                                    temperature=period['temperature'])
                          for period in hourly_content['properties']['periods']]

            self._status = 'loaded'
        except Exception as e:
            logger.exception(e)
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

    def on_load(self):
        self._status = 'ready'

