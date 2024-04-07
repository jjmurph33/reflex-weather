import reflex as rx

from .state import State

style = {
    "font_size": "16px",
}

style_button = {
    'border_radius':'1em',
    'box_shadow':'rgba(151, 65, 252, 0.8) 0 15px 30px -10px',
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
            rx.button('Lookup',style=style_button)
        ),
        on_submit=State.lookup_button_handler,
        reset_on_submit=True,
    )


def forecast_item(item: rx.Var[str]) -> rx.Component:
    return rx.list_item(
        rx.text(item),
    )


def forecast_list() -> rx.Component:
    return rx.container(
        rx.unordered_list(
            rx.foreach(State.forecast, forecast_item),
                list_style_type='none',
        )
    )

def current_weather() -> rx.Component:
    return rx.vstack(
        rx.text(f'Checking weather from {State.forecast_url}'),
        forecast_list(),
        rx.accordion.root(
            rx.accordion.item(
                header="raw data",
                content=State.raw_data,
            ),
            collapsible=True,
        )
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Weather Forecast'),
            zip_input(),
            rx.cond(State.loaded,
                    current_weather(),
                    None),
            bg=rx.color('sky'),
            padding="1em",
        ),
        height="100vh",
    )


app = rx.App(style=style)
app.add_page(index, title='Weather', on_load=State.on_load)
