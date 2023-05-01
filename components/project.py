from importlib.util import spec_from_file_location, module_from_spec
from sys import modules
from os.path import join, basename, dirname, split
from .constants import DASHBOARDS_DIR
from .funcs import get_names
from .callback import Callback
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from inspect import stack


class Project:
    def __init__(self, dashboards_to_get: list = None):
        self.project_path = stack()[1][1]
        self.id = basename(dirname(self.project_path))
        self.url = f'/{self.id}'
        self.name = self.id.replace('_', ' ').title()

        self.dashboards_path = join(split(self.project_path)[0], DASHBOARDS_DIR)
        self.all_dashboards = get_names(self.dashboards_path)
        self.dashboards_to_get = dashboards_to_get if dashboards_to_get else self.all_dashboards
        self.dashboard_objs = self._get_dashboards()

        self.app = None
        self.callbacks = []
        self.server = None

    def _get_dashboards(self) -> list:
        if set(self.dashboards_to_get).issubset(set(self.all_dashboards)):
            dashboard_objs = {}
            for dashboard_name in self.dashboards_to_get:
                dashboard_path = join(self.dashboards_path, dashboard_name + '.py')
                module_name = dashboard_path.split('.')[0]

                spec = spec_from_file_location(module_name, dashboard_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                modules[module_name] = module

                dashboard_obj = vars(module)['dashboard']
                dashboard_obj.update_dashboard(self.id, self.url)
                dashboard_objs[dashboard_obj.id] = dashboard_obj
            return dashboard_objs
        else:
            raise ValueError(f'''
                    Specified Dashboard doesn't exist. 
                    Dashboards in current's project dashboards directory are {self.all_dashboards}.
                    You've specified {self.dashboards_to_get}
            ''')

    def init_app(self):
        self.app = Dash(
            __name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SLATE],
            meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
        )
        self.app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.Nav(
                    html.Div(
                        html.Div(
                            dbc.ButtonGroup(
                                [
                                    html.Button(
                                        DashIconify(icon='teenyicons:info-small-solid', width=30),
                                        id='page-overview-toggle-btn',
                                        n_clicks=0,
                                        className='nav-button',
                                    ),
                                    html.Button(
                                        DashIconify(icon='bx:filter', width=30),
                                        id='filterpanel-toggle-btn',
                                        n_clicks=0,
                                        className='nav-button'
                                    )
                                ]
                            ),
                            className='nav-panel-buttons'
                        ),
                        className='d-flex'
                    ),
                    id='navbar',
                    className='custom-navbar'
                ),
                dbc.Modal(id='page-overview-modal', size="xl", backdrop=True, scrollable=True,
                          is_open=False, centered=True, fade=True),
                html.Div(
                    [
                        html.Div(id='filterpanel-container', className='collapsed'),
                        html.Div(id='page-content-container')
                    ],
                    id='main-div'
                )
            ],
            className='page-body'
        )

        roots = {
            dashboard_obj.url: [
                dashboard_obj.overview_modal,
                dashboard_obj.dashboard_div,
                dashboard_obj.filterpanel_comp,
            ]
            for dashboard_obj in self.dashboard_objs
        }

        def render_page(url):
            return roots[url]

        self.callbacks.append(
            Callback(
                **{
                    'outputs': [
                        ('page-overview-modal', 'children'),
                        ('page-content-container', 'children'),
                        ('filterpanel-container', 'children'),
                    ],
                    'inputs': [('url', 'pathname')],
                    'func': render_page
                }
            )
        )

        for dashboard_obj in self.dashboard_objs:
            for cb in dashboard_obj.filterpanel_values_callbacks:
                self.callbacks.append(Callback(**cb))
        for dashboard_obj in self.dashboard_objs:
            for cb in dashboard_obj.windows_callbacks:
                self.callbacks.append(Callback(**cb))
        for dashboard_obj in self.dashboard_objs:
            for filter_obj in dashboard_obj.filter_objs.values():
                if filter_obj.filter_type in ['checkbox', 'interval']:
                    self.callbacks.append(Callback(**filter_obj.filter_sync))
        for dashboard_obj in self.dashboard_objs:
            for window_obj in dashboard_obj.window_objs.values():
                for cb in window_obj.callbacks:
                    self.callbacks.append(Callback(**cb))

        def toggle_overview(clicks, is_open):
            return not is_open if clicks else is_open

        self.callbacks.append(
            Callback(
                **{
                    'outputs': [('page-overview-modal', 'is_open')],
                    'inputs': [('page-overview-toggle-btn', 'n_clicks')],
                    'states': [('page-overview-modal', 'is_open')],
                    'func': toggle_overview
                }
            )
        )

        def toggle_filterpanel(clicks, class_name):
            return "collapsed" if class_name == "toggled" else "toggled"

        self.callbacks.append(
            Callback(
                **{
                    'outputs': [('filterpanel-container', 'className')],
                    'inputs': [('filterpanel-toggle-btn', 'n_clicks')],
                    'states': [('filterpanel-container', 'className')],
                    'func': toggle_filterpanel
                }
            )
        )
        self.server = self.app.server

    def run_app(self):
        self.app.run_server(debug=True)
