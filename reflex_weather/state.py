import urllib,json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import reflex as rx

from . import location

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
    zipcode: str = rx.LocalStorage(name='zipcode')
    forecast: list[Forecast] # list of forecast periods [today, tonight, tomorrow, ...]
    hourly: list[Forecast] # list of hourly forecast periods
    last_updated: str
    _status = 'ready'

    async def lookup_button_handler(self):
        if self.zipcode:
            self._status = 'loading'
            yield
            self._check_weather()

    def _get_location(self):
        # returns the latitude and longitude for use by the weather api
        # just US zip codes for now, going to expand this later
        lat = lon = None
        (lat,lon) = location.zipdata.get(self.zipcode)
        return (lat,lon)

    def _load_weather(self,url):
        content = location.url_cache.get(url)
        if not content:
            request = urllib.request.urlopen(url)
            content = json.loads(request.read())
            logging.info('Weather content loaded')
            location.url_cache[url] = content
        else:
            logging.info('Weather content loaded from cache')
        return content

    def _load_forecast(self,url):
        content = forecast_cache.get(url)
        if not content:
            request = urllib.request.urlopen(url)
            content = json.loads(request.read())
            logging.info('Forecast data loaded')
            forecast_cache[url] = content
        else:
            logging.info('Forecast data loaded from cache')

        now = datetime.now(tz=ZoneInfo('localtime'))
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
        content = hourly_cache.get(url)
        if not content:
            request = urllib.request.urlopen(url)
            content = json.loads(request.read())
            logging.info('Hourly forecast data loaded')
            hourly_cache[url] = content
        else:
            logging.info('Hourly forecast data loaded from cache')
        return content

    def _check_weather(self):
        try:
            (lat,lon) = self._get_location()
            if not lat or not lon:
                self.error = True
                return

            url = f'https://api.weather.gov/points/{lat},{lon}'
            logging.info(f'Using location url {url}')
            weather_content = self._load_weather(url)

            forecast_url = weather_content['properties']['forecast']
            logging.info(f'Checking weather at {forecast_url}')
            forecast_content = self._load_forecast(forecast_url)

            hourly_url = weather_content['properties']['forecastHourly']
            logging.info(f'Checking hourly weather at {hourly_url}')
            hourly_content = self._load_hourly_forecast(hourly_url)

            periods = list()
            for period in forecast_content['properties']['periods']:
                start_time = datetime.fromisoformat(period['startTime'])
                f = Forecast(short=period['shortForecast'],
                             detailed=period['detailedForecast'],
                             temperature = period['temperature'],
                             icon = period['icon'],
                             period_name = period['name'],
                             )
                periods.append(f)
            self.forecast = periods

            hourly_periods = list()
            for period in hourly_content['properties']['periods']:
                start_time = datetime.fromisoformat(period['startTime'])
                f = Forecast(time=start_time.strftime('%A %-I%P'),
                             short=period['shortForecast'],
                             temperature=period['temperature'],
                             )
                hourly_periods.append(f)
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


