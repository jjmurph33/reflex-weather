import logging
import reflex as rx

from . import location
from .state import State

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

def zip_input() -> rx.Component:
    return rx.hstack(
        rx.text('Zip Code'),
        rx.input(
            name='zipcode',
            placeholder=State.zipcode,
            bg='white',
            on_blur=State.set_zipcode,
        ),
        rx.button('Lookup',style=style_button,
                  on_click=State.lookup_button_handler,
                  ),
    )

def forecast_item(data: dict) -> rx.Component:
    name = data['name']
    detail = data['detailedForecast']
    temperature = data['temperature']
    icon = data['icon']
    return rx.card(
        rx.vstack(
            rx.text.strong(name,size='4'),
            rx.text(detail,size='3'),
            rx.hstack(
                rx.image(src=icon),
                rx.vstack(
                    rx.text(f'{temperature}\u00B0',size='6'),
                    align='center',
                    justify='center'
                )
            ),
            spacing='1'
        )
    )

def forecast_list() -> rx.Component:
    return rx.vstack(
        rx.foreach(State.forecast, forecast_item),
        spacing='5'
    )

def current_weather() -> rx.Component:
    # TODO: add hourly forecast
    return rx.vstack(
        forecast_list(),
        info_sources(),
        spacing='5',
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
            rx.cond(State.is_error,display_loading_error()),
            rx.cond(State.is_loading,display_loading_message()),
            rx.cond(State.is_loaded,current_weather()),
        ),
        height="100vh",
    )

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S ', level=logging.WARN)
logging.debug('*Starting*')

location.init()
app = rx.App(style=style)
app.add_page(index, title='Weather')
