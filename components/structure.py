from dash import dcc, html
import dash_bootstrap_components as dbc
from .navbar import NavBar
from .home import Home
from .callback import Callback
from typing import Literal


class Structure:
    def __init__(self, mode: Literal['full', 'project', 'dashboard'] = 'full', project_objs: dict = None,
                 dashboard_objs: dict = None, overview_modal=None, filterpanel_comp=None, dashboard_div=None,
                 callbacks: list = None):
        self.url = dcc.Location(id="url", refresh=False)
        self.mode = mode
        self.project_objs = project_objs
        self.dashboard_objs = dashboard_objs
        if self.mode in ['full', 'project']:
            self._get_navigation_dict()
            self.home_obj = Home(navigation=self.navigation, mode=self.mode)
            self.navbar_obj = NavBar(navigation=self.navigation, mode=self.mode)
        else:
            self.navbar_obj = NavBar(mode=self.mode)
        self.layout = self._set_layout(overview_modal=overview_modal, filterpanel_comp=filterpanel_comp,
                                       dashboard_div=dashboard_div)
        self._collect_callbacks(callbacks)

    def _set_layout(self, overview_modal, filterpanel_comp, dashboard_div):
        """ Set up the layout for the app"""
        overview_modal_args = {
            'id': 'page-overview-modal', 'size': 'xl', 'backdrop': True, 'scrollable': True, 'is_open': False,
            'centered': True, 'fade': True
        }
        filterpanel_div_args = {'id': 'filterpanel-container', 'className': 'collapsed'}
        page_content_div_args = {'id': 'page-content-container'}

        if self.mode == 'dashboard':
            overview_modal_args['children'] = overview_modal
            filterpanel_div_args['children'] = filterpanel_comp
            page_content_div_args['children'] = dashboard_div

        self.overview_modal = dbc.Modal(**overview_modal_args)
        self.filterpanel_div = html.Div(**filterpanel_div_args)
        self.page_content_div = html.Div(**page_content_div_args)
        self.main_div = html.Div([self.filterpanel_div, self.page_content_div], id='main-div')

        return html.Div(
            [
                self.url,
                self.navbar_obj.nav,
                self.overview_modal,
                self.main_div
            ],
            className='page-body'
        )

    def _get_navigation_dict(self) -> None:
        if self.mode == 'full':
            self.navigation = {
                project_id: {
                    'name': project_obj.name,
                    'dashboards': {
                        dashboard_obj.url: dashboard_obj.name
                        for dashboard_obj in project_obj.dashboard_objs.values()
                    }
                }
                for project_id, project_obj in self.project_objs.items()
            }
        else:
            self.navigation = {
                dashboard_obj.url: dashboard_obj.name
                for dashboard_obj in self.dashboard_objs
            }


    def _toggle_overview(self) -> dict:
        def toggle_overview(clicks, is_open):
            return not is_open if clicks else is_open

        return {

            'outputs': [(self.overview_modal.id, 'is_open')],
            'inputs': [(self.navbar_obj.overview_button, 'n_clicks')],
            'states': [(self.overview_modal.id, 'is_open')],
            'func': toggle_overview
        }

    def _toggle_filterpanel(self) -> dict:
        def toggle_filterpanel(clicks, class_name):
            return "collapsed" if class_name == "toggled" else "toggled"

        return {
            'outputs': [(self.filterpanel_div.id, 'className')],
            'inputs': [(self.navbar_obj.filterpanel_button, 'n_clicks')],
            'states': [(self.filterpanel_div.id, 'className')],
            'func': toggle_filterpanel
        }

    def _render_page(self) -> dict:
        """ Callback to render the page when url is changed """
        output_list = [
            (self.overview_modal.id, 'children'),
            (self.page_content_div.id, 'children'),
            (self.filterpanel_div.id, 'children'),
            (self.navbar_obj.nav.id, 'style'),
            (self.page_content_div, 'style')
        ]

        roots = {
            dashboard_obj.url: [
                dashboard_obj.overview_modal,
                dashboard_obj.dashboard_div,
                dashboard_obj.filterpanel_comp,
                {},
                {},
            ]
            for project_obj in self.project_objs.values() for dashboard_obj in project_obj.dashboard_objs.values()
        }
        roots[self.home_obj.url] = [[], self.home_obj.layout, [], {'display': 'none'}, {'margin': '0'}]

        def render_page(url):
            return roots[url]

        return {
            'outputs': output_list,
            'inputs': [('url', 'pathname')],
            'func': render_page
        }

    def _collect_callbacks(self, callbacks_passed: list = None) -> None:
        callbacks = [self._toggle_overview(), self._toggle_filterpanel()]
        if self.mode in ['full', 'project']:
            callbacks.append(self._render_page())
            callbacks.extend(self.navbar_obj.callbacks)

        if self.mode == 'full':
            callbacks.extend(self.home_obj.callbacks)
            for project_obj in self.project_objs.values():
                for dashboard_obj in project_obj.dashboard_objs.values():
                    callbacks.extend(dashboard_obj.windows_callbacks + dashboard_obj.filterpanel_values_callbacks)
                    for window_obj in dashboard_obj.window_objs.values():
                        callbacks.extend(window_obj.callbacks)
                    for filter_obj in dashboard_obj.filter_objs.values():
                        callbacks.extend(filter_obj.callbacks)
        elif self.mode == 'project':
            for dashboard_obj in self.dashboard_objs.values():
                callbacks.extend(dashboard_obj.windows_callbacks + dashboard_obj.filterpanel_values_callbacks)
                for filter_obj in dashboard_obj.filter_objs.values():
                    callbacks.append(filter_obj.callback)
        else:
            callbacks.extend(callbacks_passed)
        
        self.callbacks = [Callback(**d) for d in callbacks if d is not None]
