import logging
import reflex as rx

from . import location
from .state import Weather,Forecast

logger = logging.getLogger('weather')

style_main = {
    "font_size": "16px",
}

style_button = {
    'border_radius':'1em',
    'background_image':'linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(48,85,189,1) 0%, rgba(47,76,184,1) 100%)',
    'box_sizing':'border-box',
    'color':'white',
    'opacity':1,
}

style_forecast = {
    "font_size": "18px",
    "color": "#25549d",
    "font_weight": "bold",
    "transform": "translate(10px, -4px)"
}

def zip_input() -> rx.Component:
    return rx.form(
        rx.hstack(
            rx.text('Zip Code'),
            rx.input(name='zip',
                     default_value=Weather.zipcode,
                     min_length=5,
                     max_length=5,
                     bg='white',
                     autofocus=True),
            rx.button('Lookup',
                      type='submit',
                      style=style_button
                      ),
            align='center',
        ),
        on_submit=Weather.handle_submit,
    )

def display_forecast() -> rx.Component:
    def forecast_item(forecast: Forecast) -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text.strong(forecast.period_name, size='4'),
                    rx.text(forecast.short, style=style_forecast),
                ),
                rx.hstack(
                    rx.image(src=forecast.icon),
                    rx.vstack(
                        rx.text(f'{forecast.temperature}\u00B0', size='6'),
                        rx.text(forecast.detailed, size='2'),
                        justify='center'
                    )
                ),
                spacing='1',
                border_radius='1em',
            )
        )
    return rx.vstack(
        rx.foreach(Weather.forecast, forecast_item),
        spacing='5',
        margin='5px',
    )

def display_hourly_forecast() -> rx.Component:
    def hourly_forecast_item(hourly: Forecast) -> rx.Component:
        return rx.table.row(
            rx.table.cell(hourly.time),
            rx.table.cell(rx.text.strong((f'{hourly.temperature}\u00B0')),justify='end'),
            rx.table.cell(hourly.short  ),
        )
    return rx.flex(
        rx.table.root(
            rx.table.body(
                rx.foreach(Weather.hourly, hourly_forecast_item),
            )
        ),
        margin='5px',
    )

def current_weather() -> rx.Component:
    return rx.vstack(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger('Daily', value='daily'),
                rx.tabs.trigger('Hourly', value='hourly'),
            ),
            rx.tabs.content(
                display_forecast(),
                value='daily',
            ),
            rx.tabs.content(
                display_hourly_forecast(),
                value='hourly',
            ),
            default_value='daily',
        ),
        rx.text(f'Last updated {Weather.last_updated}', size='2'),
        display_sources(),
    )

def display_sources() -> rx.Component:
    return rx.hstack(
        rx.spacer(),
        rx.text(f'weather data from weather.gov', size='1'),
        rx.text(f'zip code and location data from geonames.org', size='1'),
    )

def display_loading_error() -> rx.Component:
    return rx.text('Sorry, an error has occurred', color_scheme='red', margin='10px')

def display_loading_message() -> rx.Component:
    return rx.text('Loading...', margin='10px')

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.vstack(
                rx.heading('Weather Forecast'),
                zip_input(),
                bg=rx.color('sky'),
                border_radius='2em',
                padding='1em',
                align='center'
            ),
            rx.cond(Weather.is_error,display_loading_error()),
            rx.cond(Weather.is_loading,display_loading_message()),
            rx.cond(Weather.is_loaded,current_weather()),
        ),
        height='100vh',
        margin='5px',
    )


logger.setLevel(logging.INFO)
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',datefmt='%m/%d/%Y %I:%M:%S')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

location.init()

app = rx.App(style=style_main)
app.add_page(index, title='Weather', on_load=Weather.on_load)
logger.debug('Starting')
