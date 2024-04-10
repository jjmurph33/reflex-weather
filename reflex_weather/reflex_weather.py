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
    return rx.form(
        rx.hstack(
            rx.text('Zip Code'),
                rx.input(
                    name='zipcode',
                    placeholder=State.zipcode,
                    bg='white',
                ),
            rx.button('Lookup',style=style_button),
        ),
        on_submit=State.lookup_button_handler,
        reset_on_submit=True,
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
                    rx.text(f'{temperature} %',size='6'),
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
    return rx.vstack(
        forecast_list(),
        rx.spacer(),
        #rx.text(f'Checking weather from {State.location_url} and {State.forecast_url}',size='2'),
        #rx.spacer(),
        rx.accordion.root(
            rx.accordion.item(
                header="raw data",
                content=State.raw_data,
            ),
            collapsible=True,
        ),
        info_sources(),
        spacing='5',
    )

def info_sources() -> rx.Component:
    return rx.hstack(
        rx.text(f'weather data from weather.gov',size='1'),
        rx.text(f'zip code and location data from geonames.org',size='1'),
    )

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.vstack(
                rx.heading('Weather Forecast'),
                zip_input(),
                bg=rx.color('sky'),
                border_radius = '1em',
                padding="1em",
            ),
            rx.cond(State.loaded,
                    current_weather(),
                    None),
        ),
        height="100vh",
    )

location.init()
app = rx.App(style=style)
app.add_page(index, title='Weather', on_load=State.on_load)
