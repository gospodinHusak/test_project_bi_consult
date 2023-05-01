from dash import html, callback_context as ctx
from .constants import ABOUT_TXT, HOME_PAGE_TITLE
from typing import Literal


class Home:
    def __init__(self, navigation: dict, mode: Literal['full', 'project'] = 'full'):
        self.url = '/'
        self.navigation = navigation
        self.mode = mode
        self.callbacks = []
        self._menu()
        self.about_txt = ABOUT_TXT
        self.name = HOME_PAGE_TITLE
        self.layout = self._home_layout()
        

    def _menu(self) -> None:
        """
        Create a menu for the Home page. This function needs Home class object to know the app structure to make a valid
        menu
        """
        if self.mode == 'full':
            self.menu = html.Ul(
                id='menu',
                children=[
                    html.Li(
                        [
                            html.A(
                                project_dict['name'],
                                id=f'{project_id}-spn'
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.A(
                                                name,
                                                href=url
                                            )
                                        ]
                                    )
                                    for url, name in project_dict['dashboards'].items()
                                ],
                                id=f'{project_id}-dashboards',
                                className='hidden'
                            )
                        ]
                    )
                    for project_id, project_dict in self.navigation.items()
                ]
            )

            def open_project_list(*args) -> list or str:
                trigger_project_id = ctx.triggered[0]['prop_id'].split('.')[0].split('-')[0]
                output_target = f'{trigger_project_id}-dashboards.className'
                current_classname_value = ctx.states[output_target]
                if len(ctx.states.keys()) == 1:
                    return 'visible' if current_classname_value == 'hidden' else 'hidden'
                else:
                    ctx.states[output_target] = 'visible' if current_classname_value == 'hidden' else 'hidden'
                return [v for v in ctx.states.values()]

            outputs, inputs, states, = [], [], []
            for project_id in self.navigation.keys():
                outputs.append((f'{project_id}-dashboards', 'className'))
                inputs.append((f'{project_id}-spn', 'n_clicks'))
                states.append((f'{project_id}-dashboards', 'className'))

            self.open_project_list = {
                'outputs': outputs,
                'inputs': inputs,
                'states': states,
                'func': open_project_list
            }
            self.callbacks.append(self.open_project_list)

        else:
            self.menu = html.Ul(
                id='menu',
                children=[
                    html.Li(
                        [
                            html.A(
                                name,
                                href=url
                            )
                        ]
                    )
                    for url, name in self.navigation_dict.items()
                ],
                className='hidden'

            )

    def _navigation_panel(self) -> html.Div:
        """ Create navigation panel with Home page menu """
        return html.Div(
            [
                html.H3('Pages', id='menu-title'),
                html.Hr(),
                self.menu
            ],
            className='navigation-panel'
        )

    def _about(self) -> html.Div:
        """ Read the "About" information and creates the container with the text """
        paragraphs = self.about_txt.split('\n')
        text = [html.P(paragraph, className='p-2') for paragraph in paragraphs]
        return html.Div(
            [
                html.H3('About', className='label-home-page'),
                html.Div(text, className='about-text'),
            ],
            className='about-div'
        )

    def _home_layout(self) -> html.Div:
        """ Set up Home page layout """
        return html.Div(
            [
                html.H2(self.name, className='title'),
                html.Div(
                    [
                        self._navigation_panel(),
                        self._about()
                    ],
                    className='main'
                )
            ]
        )

