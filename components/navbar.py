from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify


class NavBar:
    def __init__(self, mode, navigation: dict = None):
        self.navigation = navigation
        self.nav_menu_items_container = dbc.Nav(horizontal='start', id='menu-items-container')
        self.nav_menu_div = html.Div(self.nav_menu_items_container, id='dashboards-menu', className='dropdown-menu')
        self.nav_menu_button = html.Button(id='pages_list-btn')
        self.overview_button = self._overview_button()
        self.filterpanel_button = self._filterpanel_button()
        if mode in ['full', 'project']:
            self.content = [
                self._home_button(),
                self._pages_dropdown(),
                self._button_group()
            ]
            self.callbacks = [
                self._change_nav_menu_label(),
                self._toggle_nav_menu(),
                self._fill_nav_menu(),
            ]
        else:
            self.content = [self._button_group()]
        self.nav = self._navbar()

    @staticmethod
    def _home_button() -> html.A:
        return html.A(
            DashIconify(icon='ci:home-alt-fill', width=50),
            id='home-btn',
            href='/',
            className='home-button'
        )

    @staticmethod
    def _overview_button() -> html.Button:
        return html.Button(
            DashIconify(icon='teenyicons:info-small-solid', width=30),
            id='page-overview-toggle-btn',
            n_clicks=0,
            className='nav-button',
        )

    @staticmethod
    def _filterpanel_button() -> html.Button:
        return html.Button(
            DashIconify(icon='system-uicons:filtering', width=30),
            id='filterpanel-toggle-btn',
            n_clicks=0,
            className='nav-button'
        )

    def _pages_dropdown(self) -> html.Div:
        return html.Div(
            [
                self.nav_menu_button,
                self.nav_menu_div
            ],
            className='pages-dropdown'
        )

    def _button_group(self) -> html.Div:
        return html.Div(
            dbc.ButtonGroup(
                [
                    self.overview_button,
                    self.filterpanel_button
                ]
            ),
            className='nav-panel-buttons'
        )

    def _navbar(self) -> html.Nav:
        return html.Nav(
            html.Div(
                self.content,
                className='d-flex'
            ),
            id='navbar',
            className='custom-navbar'
        )

    def _change_nav_menu_label(self) -> dict:
        """
        Callback updates the menu label (basically it sets the name of the current dashboard)
        """

        def change_nav_menu_label(inp_url):
            if inp_url == '/':
                return ''
            target_project_id = inp_url.split('/')[1]
            return self.navigation[target_project_id]['dashboards'][inp_url]

        return {
            'outputs': [(self.nav_menu_button.id, 'children')],
            'inputs': [('url', 'pathname')],
            'func': change_nav_menu_label,
        }

    def _toggle_nav_menu(self) -> dict:
        """
        Callback that opens a list of featured dashboards of the current project you're in.
        It switches style attribute's parameter "display" between "block" (show) and "none" (hide)
        """

        def toggle_nav_menu(clicks, class_name):
            return 'dropdown-menu show' if class_name == 'dropdown-menu' else 'dropdown-menu'

        return {
            'outputs': [(self.nav_menu_div.id, 'className')],
            'inputs': [(self.nav_menu_button.id, 'n_clicks')],
            'states': [(self.nav_menu_div.id, 'className')],
            'func': toggle_nav_menu
        }

    def _fill_nav_menu(self) -> dict:
        """
        Callback that updates dashboards dropdown menu if it's needed. So each time when you move to another page this
        callback checks whether you've switched t another project. If so it updates the dropdown menu, otherwise it
        raises exception PreventUnpdate and nothing happens.
        """

        def fill_nav_menu(inp_url):
            if inp_url == '/':
                return []
            else:
                input_project_id = inp_url.split('/')[1]
                dashboard_links = self.navigation[input_project_id]['dashboards']
                return [
                    dbc.NavItem(
                        dbc.NavLink(
                            name,
                            href=url,
                            class_name='link'
                        )
                    )
                    for url, name in dashboard_links.items()
                ]

        return {
            'outputs': [(self.nav_menu_items_container.id, 'children')],
            'inputs': [('url', 'pathname')],
            'func': fill_nav_menu
        }
