from typing import Literal, Union
from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc


class Filter:
    def __init__(self, dashboard_id: str, datasource_id: str, source_column: str, columns_config: dict, name: str = None,
                 filter_type: Literal['checkbox', 'radio', 'interval', 'daterange'] = 'checkbox',
                 default_value: Union[list, int, str] = None, target_windows: list = None):
        if source_column not in columns_config.keys():
            raise ValueError(f'''
                There is no column {source_column} in datasource filter columns.
                Please use on of the datasource filter columns that you've specified when created Datasource object.
                Current filter columns for connected datasource are {columns_config.keys()}
            ''')

        self.dashboard_id = dashboard_id
        self.datasource_id = datasource_id
        self.source_column = source_column
        self.name = name if name else self.source_column.replace('_', ' ').title()
        self.id = self.name.lower().replace(' ', '_')
        self._set_id_prefix()
        self._set_component_id()
        self.filter_type = filter_type
        self.values_config = columns_config[self.source_column]
        self.target_windows = target_windows if target_windows else []
        self._set_default_value(default_value)
        self.callbacks = []
        self._create_item()
        self._filter_sync()
        self._query_expression()

    def _set_id_prefix(self, project_id: str = None):
        dash_filter = f"{self.dashboard_id}-{self.id}"
        self.id_prefix = dash_filter if not project_id else f"{project_id}-{dash_filter}"

    def _set_component_id(self):
        self.component_id = f"{self.id_prefix}-filter"

    def _validate_value_type(self, target_value: str) -> bool:
        if self.filter_type == 'radio':
            if not isinstance(target_value, (int, str)):
                raise TypeError('Default value for radio filter should be of type int or str')
        elif self.filter_type in ['checkbox', 'interval', 'daterange']:
            if not isinstance(target_value, list):
                raise TypeError(f'Default value for {self.filter_type} filter should be of type list')
        return True

    def _validate_value_existence(self, target_value: Union[list, int, str], column_values: set) -> bool:
        target_value = [target_value] if isinstance(target_value, (int, str)) else target_value
        if not set(target_value).issubset(column_values):
            raise ValueError(f'''Value(s) for default_value not found in column '{self.source_column}'.''')
        else:
            return True

    def _set_default_value(self, default_value = None) -> list or int or str:
        values_set = set(self.values_config) if type(self.values_config) == list else set(self.values_config.keys())
        if default_value:
            if self._validate_value_type(default_value) and self._validate_value_existence(default_value, values_set):
                self.default_value = default_value
        else:
            if self.filter_type == 'radio':
                self.default_value = min(values_set)
            elif self.filter_type == 'checkbox':
                self.default_value = list(values_set)
            elif self.filter_type in ['interval', 'daterange']:
                self.default_value = [min(values_set), max(values_set)]

    def _set_options(self) -> list or None:
        if self.filter_type in ('checkbox', 'radio'):
            if type(self.values_config) == dict:
                return [{"label": label, "value": value} for label, value in self.values_config.items()]
            else:
                return [{"label": value, "value": value} for value in self.values_config]
        else:
            return None

    def _checkbox(self) -> list[dbc.Checklist]:
        all_value_item = dbc.Checklist(
            id=self.component_id + "-all-value",
            options=[{"label": "All", "value": "All"}],
            value=['All'],
            persistence=True,
            persistence_type="session",
            class_name='all-value-option filter'
        )
        listed_values_item = dbc.Checklist(
            id=self.component_id,
            options=self._set_options(),
            value=self.default_value,
            persistence=True,
            persistence_type="session",
            class_name='filter'
        )
        return [all_value_item, listed_values_item]

    def _radio(self) -> dcc.RadioItems:
        return dcc.RadioItems(
            id=self.component_id,
            options=self._set_options(),
            value=self.default_value,
            className='filter'
        )

    def _interval(self) -> html.Div:
        minv, maxv = self.default_value
        return html.Div(
            [
                dcc.Input(
                    id=self.component_id + f'-min-input',
                    type='number',
                    value=minv,
                    className='interval-input'
                ),
                dcc.RangeSlider(
                    id=self.component_id,
                    marks=None,
                    min=minv,
                    max=maxv,
                    value=self.default_value,
                    allowCross=False,
                    updatemode='drag',
                    className='interval-slider'
                ),
                dcc.Input(
                    id=self.component_id + f'-max-input',
                    type='number',
                    value=maxv,
                    className='interval-input'
                ),
            ],
            className='interval-components'
        )
    
    def _date_range_picker(self):
        minv, maxv = self.default_value
        return dcc.DatePickerRange(
            id=self.component_id,
            calendar_orientation='vertical',
            first_day_of_week=1,
            display_format='DD.MM.YYYY',
            min_date_allowed=minv,
            max_date_allowed=maxv,
            start_date=minv,
            stay_open_on_select=True,
            end_date=maxv,
            className='date-range-picker'
        )

    def _create_item(self) -> None:
        func_config = {
            "checkbox": self._checkbox, 
            "radio": self._radio, 
            "interval": self._interval,
            "daterange": self._date_range_picker
        }
        self.filter = dbc.AccordionItem(
            children=func_config[self.filter_type](),
            title=self.name,
            class_name=self.filter_type
        )

    def _query_expression(self) -> None:
        queries = {
            "checkbox": self.source_column + ' in {value}',
            "radio": self.source_column + ' == {value}',
            "interval": self.source_column + ' >= {value[0]} and ' + self.source_column + ' <= {value[1]}',
            "daterange": self.source_column + ' >= "{value[0]}" and ' + self.source_column + ' <= "{value[1]}"'
        }
        self.query_expression = queries[self.filter_type]

    def _filter_sync(self) -> None:
        if self.filter_type == 'interval':
            def interval_sync_callback(*args):
                ctx = callback_context
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if trigger_id.endswith("input"):
                    if 'min' in trigger_id:
                        min_value = ctx.triggered[0]['value']
                        max_value = ctx.states[self.component_id + '-max-input.value']
                    else:
                        max_value = ctx.triggered[0]['value']
                        min_value = ctx.states[self.component_id + '-min-input.value']
                    range_values = [min_value, max_value]
                else:
                    range_values = ctx.triggered[0]['value']
                    min_value = range_values[0]
                    max_value = range_values[1]
                return range_values, min_value, max_value
            self.filter_sync = {
                'outputs': [
                    (self.component_id, 'value'),
                    (self.component_id + '-min-input', 'value'),
                    (self.component_id + '-max-input', 'value')
                ],
                'inputs': [
                    (self.component_id, 'value'),
                    (self.component_id + '-min-input', 'value'),
                    (self.component_id + '-max-input', 'value')
                ],
                'states': [
                    (self.component_id + '-min-input', 'value'),
                    (self.component_id + '-max-input', 'value')
                ],
                'func': interval_sync_callback
            }
            self.callbacks.append(self.filter_sync)

        if self.filter_type == 'checkbox':
            def checkbox_sync_callback(listed_val, all_val, state_val, options):
                ctx = callback_context
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
                trigger_options = [d['value'] for d in ctx.states[f'{self.component_id}.options']]
                if trigger_id.endswith("all-value"):
                    all_value = ctx.triggered[0]['value']
                    checklist_vals = trigger_options if all_value else []
                else:
                    checklist_vals = ctx.triggered[0]['value']
                    all_value = ['All'] if set(checklist_vals) == set(trigger_options) else []
                return checklist_vals, all_value
            self.filter_sync = {
                'outputs': [(self.component_id, 'value'), (self.component_id + '-all-value', 'value'), ],
                'inputs': [(self.component_id, 'value'), (self.component_id + '-all-value', 'value')],
                'states': [(self.component_id, 'value'), (self.component_id, 'options')],
                'initial_call': False,
                'func': checkbox_sync_callback
            }
            self.callbacks.append(self.filter_sync)

    def update_ids(self, project_id) -> None:
        self._set_id_prefix(project_id)
        self._set_component_id()
        self._create_item()

        if self.filter_type in ['checkbox', 'interval']:
            self._filter_sync()
