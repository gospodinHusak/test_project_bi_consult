from os import path
from dash import Dash, html, dcc, callback_context as ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from .funcs import get_clear_args, to_dependencies
from .filter import Filter
from .parameter import Parameter
from .window import Window
from .datasource import DataSource
from .app import App
from inspect import stack



class Dashboard:
    def __init__(self, datasource_objs: list[DataSource], overview_text: str = None, name: str = None):
        self.dashboard_path = stack()[1][1]
        self.id = path.basename(self.dashboard_path).split('.')[0]
        self._set_id_prefix()
        self._set_url()

        self.name = name if name else self.id.replace('_', ' ').title()
        self.datasource_objs = {ds.id: ds for ds in datasource_objs}

        self.filter_objs = {}
        self.parameter_objs = {}
        self.window_objs = {}

        self.dashboard_div = None
        self.filterpanel_values_callbacks = None
        self.windows_callbacks = []

        self._set_overview_modal(overview_text)
        self._apply_button()
        self._filterpanel()

        self.app = None

    def _set_id_prefix(self, project_id: str = None):
        dashboard_id = self.id
        self.id_prefix = dashboard_id if not project_id else f"{project_id}-{dashboard_id}"

    def _set_url(self, project_url: str = None):
        dashboard_url = f"/{self.id}"
        self.url = dashboard_url if not project_url else f"{project_url}{dashboard_url}"

    def _set_overview_modal(self, overview_text) -> None:
        overview_modal = [dbc.ModalHeader(html.Strong(f"{self.name} Dashboard Overview"), className='overview-header')]
        if overview_text:
            paragraphs = (
                ''.join(
                    [
                        element if element != '' else '\n'
                        for element in [i.lstrip() for i in overview_text.split('\n')]
                    ]
                )
            ).split('\n')
            for paragraph in paragraphs:
                overview_modal.append(html.P(paragraph, className='p-2'))
        else:
            overview_modal.append(
                html.P("Overview is not prepared yet. Expect to see it in future versions", className='p-2')
            )
        self.overview_modal = overview_modal

    def _apply_button(self) -> None:
        self.apply_button_id = f"{self.id_prefix}-apply_filters_button"
        self.apply_button_comp = html.Button(
            children=[
                html.Span('APPLY FILTERS', className='apply-filters-text', n_clicks=0, id=self.apply_button_id),
            ],
            className="apply-filters-btn"
        )

    def _filterpanel(self) -> None:
        self.filterpanel_id = f"{self.id_prefix}-filterpanel"
        components = [filter_obj.filter for filter_obj in self.filter_objs.values()]
        if len(self.parameter_objs) > 0:
            parameters = [parameter_obj.parameter for parameter_obj in self.parameter_objs.values()]
            components.extend(parameters)
        self.filterpanel_comp = html.Div(
            id=self.filterpanel_id,
            children=[dbc.Accordion(components, flush=True), self.apply_button_comp],
            className='collapsed'
        )

    def _callback_filterpanel_values(self) -> None:
        if len(self.window_objs.keys()) >= 1:
            callbacks_dicts = []

            def filterpanel_values(*args):
                filters_vals_dict = {}
                for k, v in ctx.states.items():
                    key = k.split('.')[0]
                    if key not in filters_vals_dict.keys():
                        filters_vals_dict[key] = v
                    else:
                        filters_vals_dict[key] = [filters_vals_dict[key], v]

                parameters_vals_dict = {
                    k.split('.')[0].split('-')[-1]: v for k, v in ctx.states.items() if 'parameter' in k
                }
                query_parts = {ds_id: [] for ds_id in self.datasource_objs.keys()}
                for k, v in filters_vals_dict.items():
                    for component_id, obj in self.filter_objs.items():
                        if k == component_id and \
                                (window_obj.id in obj.target_windows or obj.target_windows == []):
                            if '==' in obj.query_expression and isinstance(v, str):
                                v = f'"{v}"'
                            query_parts[obj.datasource_id].append(obj.query_expression.format(value=v))
                query_expressions = {ds_id: ' & '.join(parts) for ds_id, parts in query_parts.items()}
                return {'query_expressions': query_expressions, 'parameters': parameters_vals_dict}

            for window_obj in self.window_objs.values():
                store = window_obj.filterpanel_values_store_id
                states = []
                for filter_obj in self.filter_objs.values():
                    if filter_obj.filter_type != 'daterange':
                        states.append((filter_obj.component_id, 'value'))
                    else:
                        states.append((filter_obj.component_id, 'start_date'))
                        states.append((filter_obj.component_id, 'end_date'))
                for param_obj in self.parameter_objs.values():
                    states.append((param_obj.component_id, 'value'))
                callbacks_dicts.append(
                    {
                        'outputs': [(store, 'data')],
                        'inputs': [(self.apply_button_id, 'n_clicks')],
                        'states': states,
                        'func': filterpanel_values,
                        'initial_call': True,
                    }
                )
            self.filterpanel_values_callbacks = callbacks_dicts
        else:
            pass

    def _prepare_window_callbacks(self) -> None:
        window_callbacks = []
        for cb in self.windows_callbacks:
            cb['outputs'] = to_dependencies(self.id_prefix, cb['outputs'])
            cb['inputs'] = to_dependencies(self.id_prefix, cb['inputs'])
            if cb['states']:
                cb['states'] = to_dependencies(self.id_prefix, cb['states'])
            window_callbacks.append(cb)
        self.windows_callbacks = window_callbacks

    def _dashboard(self) -> None:
        self.dashboard_div = html.Div(
            id=self.id_prefix,
            children=[window_obj.window_comp for window_obj in self.window_objs.values()],
            className='dashboard-div'
        )

    def add_filter(self, datasource_id: str, source_column: str, name: str = None,
                   filter_type: Literal['checkbox', 'radio', 'interval', 'daterange'] = 'checkbox',
                   default_value = None, target_windows: list = None) -> None:
        filter_obj = Filter(
            columns_config=self.datasource_objs[datasource_id].columns_config,
            dashboard_id=self.id,
            **get_clear_args(locals())
        )
        self.filter_objs[filter_obj.component_id] = filter_obj
        self._filterpanel()
        self._callback_filterpanel_values()

    def add_parameter(self, name: str, options: dict, default_value,
                      parameter_type: Literal['negative_positive'] = 'negative_positive') -> None:
        parameter_obj = Parameter(dashboard_id=self.id, **get_clear_args(locals()))
        self.parameter_objs[parameter_obj.component_id] = parameter_obj
        self._filterpanel()
        self._callback_filterpanel_values()

    def add_window(self, window_id: int, name: str, row_start: int, row_end: int, col_start: int, col_end: int,
                   remove_buttons: list = None, layout: dict = None, info: str = None,
                   table_feature: bool = False, content_type: Literal['graph', 'table'] = 'graph') -> None:
        window_obj = Window(dashboard_id=self.id, **get_clear_args(locals()))
        self.window_objs[window_id] = window_obj
        self._dashboard()
        self._callback_filterpanel_values()

    def set_callback(self, func, outputs: dict, inputs: dict, states: dict = None, initial_call: bool = False) -> None:
        self.windows_callbacks.append(
            {
                'outputs': outputs,
                'inputs': inputs,
                'states': states,
                'func': func,
                'initial_call': initial_call
            }
        )

    def update_dashboard(self, project_id: str, project_url: str) -> None:
        self._set_id_prefix(project_id)
        self._set_url(project_url)

        for window_obj in self.window_objs.values():
            window_obj.update_ids(project_id)
        for filter_obj in self.filter_objs.values():
            filter_obj.update_ids(project_id)
        for parameter_obj in self.parameter_objs.values():
            parameter_obj.update_ids(project_id)

        self.filter_objs = {filter_obj.component_id: filter_obj for filter_obj in self.filter_objs.values()}

        self._apply_button()
        self._filterpanel()
        self._dashboard()
        self._prepare_window_callbacks()
        self._callback_filterpanel_values()

    def init_app(self):
        self._prepare_window_callbacks()

        callbacks = self.filterpanel_values_callbacks + self.windows_callbacks
        for window_obj in self.window_objs.values():
            callbacks.extend(window_obj.callbacks)
        for filter_obj in self.filter_objs.values():
            callbacks.extend(filter_obj.callbacks)

        self.app = App(mode='dashboard', dashboard_div=self.dashboard_div, filterpanel_comp=self.filterpanel_comp,
                       overview_modal=self.overview_modal, callbacks=callbacks)
        self.app.run_app()

        
