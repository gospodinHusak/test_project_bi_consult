from dash import Dash
from .structure import Structure
from .funcs import get_names
from dash_bootstrap_components.themes import SLATE
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from importlib.util import spec_from_file_location, module_from_spec
from sys import modules
from os import path
from inspect import stack


class App:
    def __init__(self, mode: Literal['full', 'project', 'dashboard'] = 'full', projects_to_get: list = None,
                 dashboard_objs: dict = None, dashboard_div=None, filterpanel_comp=None, overview_modal=None,
                 callbacks: list = None):
        self.app = Dash(
            __name__, suppress_callback_exceptions=True, external_stylesheets=[SLATE],
            meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
        )
        self._get_structure(mode=mode, projects_to_get=projects_to_get, dashboard_objs=dashboard_objs,
                            overview_modal=overview_modal, filterpanel_comp=filterpanel_comp,
                            dashboard_div=dashboard_div, callbacks=callbacks)
        self.app.layout = self.structure_obj.layout
        self.server = self.app.server

    def _get_projects(self) -> dict:
        """
        Gets the projects objects. If you specify a list of projects you want to read from projects directory,
        a validity check is carried out on the defined projects. If all of the listed project names
        (the names of the directories where the individual projects reside) are valid, then the import of Project class
        objects, which are defined in separate project.py files, is performed and each such object is placed in the list
        """
        if set(self.projects_to_get).issubset(set(self.all_projects)):
            project_objs = {}
            for project in self.projects_to_get:
                project_path = path.join(self.projects_path, project, 'project.py')
                spec = spec_from_file_location('project', project_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                modules['project'] = module
                project_obj = vars(module)['project']
                project_objs[project_obj.id] = project_obj
            return project_objs
        else:
            raise ValueError(f'''
                    Specified Project doesn't exist. 
                    Projects in projects directory are {self.all_projects}.
                    You've specified {self.projects_to_get}
            ''')

    def _get_structure(
            self, mode: Literal['full', 'project', 'dashboard'] = 'full', projects_to_get: list = None,
            dashboard_objs: dict = None, filterpanel_comp=None, dashboard_div=None, overview_modal=None,
            callbacks: list = None
    ) -> None:
        if mode == 'full':
            self.projects_path = path.join(path.split(stack()[2][1])[0], 'projects')
            self.all_projects = get_names(self.projects_path)
            self.projects_to_get = projects_to_get if projects_to_get else self.all_projects
            self.project_objs = self._get_projects()
            self.structure_obj = Structure(mode=mode, project_objs=self.project_objs)
        elif mode == 'project':
            self.dashboard_objs = dashboard_objs
            self.structure_obj = Structure(mode=mode, dashboard_objs=self.dashboard_objs)
        else:
            self.structure_obj = Structure(
                mode=mode, overview_modal=overview_modal, filterpanel_comp=filterpanel_comp,
                dashboard_div=dashboard_div, callbacks=callbacks
            )

    def run_app(self):
        self.app.run_server(debug=True)
