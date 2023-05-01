from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from .constants import EMPTY_LAYOUT, MODEBAR_BUTTONS, META_BUTTONS, TABLE_STYLE_CELL, TABLE_STYLE_HEADER
from .funcs import merge_children
try:
    from typing import Litera
except ImportError:
    from typing_extensions import Literal


class Window:
    def __init__(self, dashboard_id: str, window_id: int, name: str, row_start: int, row_end: int, col_start: int,
                 col_end: int, remove_buttons: list = None, layout: dict = None, info: str = None,
                 table_feature: bool = False, content_type: Literal['graph', 'table'] = 'graph'):
        self.dashboard_id = dashboard_id
        self.id = window_id
        self.name = name
        self.info_text = 'Graph info is WIP.' if not info else info
        self.table_feature = table_feature
        self.buttons = []
        self.features = []
        self.callbacks = []
        self.layout = EMPTY_LAYOUT if not layout else layout
        self.remove_buttons = remove_buttons if remove_buttons else []
        self.window_config = {
            'grid-row-start': str(row_start),
            'grid-row-end': str(row_end),
            'grid-column-start': str(col_start),
            'grid-column-end': str(col_end),
        }

        self._set_id_prefix()
        self._label()

        self.content_type = content_type
        if self.content_type == 'graph':
            self._graph()
        else:
            self._table()

        self._filterpanel_values()
        self._info()
        if self.table_feature:
            self._meta_table()
        self._create_window()

    def _set_id_prefix(self, project_id: str = None):
        dash_window = f"{self.dashboard_id}-{self.id}"
        self.id_prefix = dash_window if not project_id else f"{project_id}-{dash_window}"

    @staticmethod
    def _validate_modebar_buttons(buttons) -> bool:
        if buttons:
            if not set(buttons).issubset(MODEBAR_BUTTONS):
                raise ValueError(f'''
                    Some of the buttons specified are invalid. There are correct values: {MODEBAR_BUTTONS}
                ''')
        return True

    def _label(self) -> None:
        self.label_comp = html.Div(html.H2(self.name, className="graph-label"), className='label-row')

    def _graph(self) -> None:
        self.graph_id = f"{self.id_prefix}-graph"
        self.content_comp = dcc.Graph(
            id=self.graph_id,
            figure=go.Figure(layout=self.layout),
            config={
                "scrollZoom": True,
                "modeBarButtonsToRemove": self.remove_buttons
            },
            responsive=True,
            className='graph'
        )

    def _table(self) -> None:
        self.graph_id = f"{self.id_prefix}-table"
        self.content_comp = html.Div(
            dash_table.DataTable(
                id=self.graph_id,
                style_cell={
                    'textAlign': 'center',
                    'backgroundColor': 'transparent',
                    'color': '#EBEBF5',
                    'border': '1px solid #14141e',
                },
                style_table={
                    'height': '100%',
                    'width': '100%'
                },
                style_header={
                    'backgroundColor': 'transparent',
                    'color': '#ff4401',
                    'fontWeight': 'bold',
                    'border': '1px solid #14141e'
                },
                style_data_conditional=[],
                row_selectable='multi',
                cell_selectable=False,
                page_size=10,
                merge_duplicate_headers=True,
            ),
            className='graph'
        )

    def _filterpanel_values(self):
        self.filterpanel_values_store_id = f"{self.id_prefix}-filterpanel_values_store"
        self.filterpanel_values_store_comp = dcc.Store(id=self.filterpanel_values_store_id)

    def _info(self) -> None:
        self.info_button_id = f"{self.id_prefix}-info_button"
        self.info_popover_id = f"{self.id_prefix}-info_popover"
        self.info_button_comp = html.Button(
            id=self.info_button_id, children=DashIconify(icon=META_BUTTONS['info'], width=30), n_clicks=0,
            className='little-button'
        )
        self.info_popover_comp = dbc.Popover(
            id=self.info_popover_id, children=self.info_text,
            target=self.info_button_id, is_open=False,
            placement='right-start', trigger="click", hide_arrow=True, class_name='info-popover'
        )

        self.buttons.append(self.info_button_comp)
        self.features.append(self.info_popover_comp)

    def _meta_table(self) -> None:
        self.table_modal_id = f"{self.id_prefix}-table_modal"
        self.table_button_id = f"{self.id_prefix}-table_button"
        self.table_store_id = f"{self.id_prefix}-table_store"
        self.table_button_comp = html.Button(
            DashIconify(icon=META_BUTTONS['data_table'], width=30),
            id=self.table_button_id,
            n_clicks=0,
            className='little-button'
        )
        self.table_store_comp = dcc.Store(id=self.table_store_id)
        self.table_modal_comp = dbc.Modal(
            id=self.table_modal_id, size="xl", backdrop=True, scrollable=True, is_open=False, centered=True, fade=True
        )

        self.buttons.append(self.table_button_comp)
        self.features.append(self.table_store_comp)
        self.features.append(self.table_modal_comp)

        def table_show(nclicks, data):
            if data:
                table = dash_table.DataTable(data['table'], style_cell=TABLE_STYLE_CELL, style_header=TABLE_STYLE_HEADER)
                return True, table
            else:
                return True, html.P("No data yet")
        self.callbacks.append(
            {
                'outputs': [(self.table_modal_id, 'is_open'), (self.table_modal_id, 'children')],
                'inputs': [(self.table_button_id, 'n_clicks')],
                'states': [(self.table_store_id, 'data')],
                'func': table_show
            }
        )

    def _create_window(self):
        self.window_comp_id = f"{self.id_prefix}-window"
        self.button_group = [dbc.ButtonGroup(self.buttons, vertical=True, class_name='btn-grp-aaa')]
        self.window_comp = html.Div(
            id=self.window_comp_id,
            children=[
                self.label_comp,
                html.Div(
                    merge_children(
                        [
                            self.features,
                            self.button_group,
                            self.content_comp
                        ]
                    ),
                    className='graph-row'
                ),
                self.filterpanel_values_store_comp
            ],
            style=self.window_config,
            className='window',
        )

    def update_ids(self, project_id) -> None:
        self._set_id_prefix(project_id)
        self.buttons = []
        self.features = []
        self.callbacks = []

        self._label()

        if self.content_type == 'graph':
            self._graph()
        else:
            self._table()

        self._filterpanel_values()
        self._info()

        if self.table_feature:
            self._meta_table()

        self._create_window()
