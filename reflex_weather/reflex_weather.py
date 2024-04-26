import logging
from datetime import datetime
import reflex as rx

from . import location
from .state import Weather,Forecast

style = {
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
    "transform": "translate(5px, -5px)"
}

def zip_input() -> rx.Component:
    return rx.hstack(
        rx.text('Zip Code'),
        rx.input(
            name='zipcode',
            placeholder=Weather.zipcode,
            bg='white',
            on_blur=Weather.set_zipcode,
        ),
        rx.button('Lookup',style=style_button,
                  on_click=Weather.lookup_button_handler,
                  ),
    )

def forecast_item(forecast: dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text.strong(forecast['name'],size='4'),
                rx.text(forecast['shortForecast'], style=style_forecast),
            ),
            rx.hstack(
                rx.image(src=forecast['icon']),
                rx.vstack(
                    rx.text(f'{forecast["temperature"]}\u00B0',size='6'),
                    rx.text(forecast['detailedForecast'], size='2'),
                    justify='center'
                )
            ),
            spacing='1',
            border_radius='1em',
        )
    )

def forecast_list() -> rx.Component:
    return rx.vstack(
        rx.foreach(Weather.forecast, forecast_item),
        spacing='5'
    )

def hourly_forecast() -> rx.Component:
    def hourly_forecast_item(hourly: Forecast) -> rx.Component:
        return rx.hstack(
            rx.text(hourly.time),
            rx.text(hourly.short),
            rx.text(f'{hourly.temperature}\u00B0'),
        )
    return rx.card(
        rx.vstack(
            rx.foreach(Weather.hourly, hourly_forecast_item),
            spacing='1'
        )
    )

def current_weather() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Daily", value="daily"),
            rx.tabs.trigger("Hourly", value="hourly"),
        ),
        rx.tabs.content(
            rx.vstack(
                forecast_list(),
                info_sources(),
                spacing='5',
            ),
            value="daily",
        ),
        rx.tabs.content(
            rx.vstack(
                hourly_forecast(),
                info_sources(),
            ),
            value="hourly",
        ),
        default_value="daily",
    )



def info_sources() -> rx.Component:
    return rx.hstack(
        rx.spacer(),
        rx.text(f'weather data from weather.gov',size='1'),
        rx.text(f'zip code and location data from geonames.org',size='1'),
    )

def display_loading_error() -> rx.Component:
    return rx.text('Sorry, an error has occurred')

def display_loading_message() -> rx.Component:
    return rx.text('Loading...')

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.vstack(
                rx.heading('Weather Forecast'),
                zip_input(),
                bg=rx.color('sky'),
                border_radius = '2em',
                padding='1em',
            ),
            rx.cond(Weather.is_error,display_loading_error()),
            rx.cond(Weather.is_loading,display_loading_message()),
            rx.cond(Weather.is_loaded,current_weather()),
        ),
        height='100vh',
        margin='5px',
    )

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S ', level=logging.INFO)
logging.debug('*Starting*')

location.init()
app = rx.App(style=style)
app.add_page(index, title='Weather')
