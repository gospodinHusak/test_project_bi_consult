try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from dash import dcc
from dash.html import Param
import dash_bootstrap_components as dbc


class Parameter:
    def __init__(self, dashboard_id: str, name: str, options: dict, default_value,
                 parameter_type: Literal['negative_positive']):
        self.dashboard_id = dashboard_id
        self.name = name
        self.id = self.name.lower().replace(' ', '_')
        self._set_id_prefix()
        self.parameter_type = parameter_type
        self.component_id = f"{self.dashboard_id}-{self.id}-parameter-{self.parameter_type}"
        self.options = [{"label": label, "value": value} for label, value in options.items()]
        self.default_value = default_value
        self._create_item()

    def _set_id_prefix(self, project_id: str = None):
        dash_param = f"{self.dashboard_id}-{self.id}"
        self.id_prefix = dash_param if not project_id else f"{project_id}-{dash_param}"

    def _radio(self) -> dcc.RadioItems:
        return dcc.RadioItems(
            id=self.component_id,
            options=self.options,
            value=self.default_value,
            className='filter'
        )

    def _create_item(self) -> None:
        func_config = {
            "negative_positive": self._radio, 
        }
        self.parameter = dbc.AccordionItem(
            children=func_config[self.parameter_type](),
            title=self.name,
            class_name=self.parameter_type
        )

    def update_ids(self, project_id) -> None:
        self._set_id_prefix(project_id)
        self.component_id = f"{self.id_prefix}-parameter-{self.parameter_type}"
        self._create_item()
