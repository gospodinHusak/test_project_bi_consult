from os.path import dirname, join, isfile, split
from inspect import stack
import pandas as pd


class DataSource:
    def __init__(self, filename: str, filter_columns: dict, rename_cols: dict = None, sep=None, set_date_columns: dict = None):
        self.id, self.extension = filename.split('.')
        self.root_dir = dirname(dirname(__file__))
        self.path = join(self.root_dir, split(stack()[1][1])[0], 'data', filename)
        self.read_args = {}
        if sep:
            self.read_args['sep'] = sep
        self.dataframe = self._read_data()
        if rename_cols:
            self.dataframe.rename(columns=rename_cols, inplace=True)
        if set_date_columns:
            for col, dt_format in set_date_columns.items():
                self.dataframe[col] = pd.to_datetime(self.dataframe[col], format=dt_format).dt.strftime('%Y-%m-%d')
        self.columns_config = self._set_columns_config(filter_columns)

    def _read_data(self) -> pd.DataFrame:
        supported_extensions = {'csv': pd.read_csv, 'parquet': pd.read_parquet}
        if self.extension in supported_extensions.keys():
            if isfile(self.path):
                return supported_extensions[self.extension](self.path, **self.read_args)
            else:
                raise ValueError(f'''
                    Given file doesn't exist in datasources directory: {join(self.root_dir, split(stack()[2][1])[0], 'data')}
                ''')
        else:
            raise TypeError(f'''
                    Extension {self.extension} not supported. Supported extensions are: {supported_extensions.keys()}
                ''')
    
    def _get_column_minmax(self, column):
        return self.dataframe[column].sort_values().agg(['min', 'max']).tolist()

    def _get_column_unique(self, column):
        return sorted(self.dataframe[column].unique().tolist())

    def _set_columns_config(self, columns: dict) -> dict:
        rules = {
            'minmax': self._get_column_minmax, 
            'unique': self._get_column_unique,
        }
        return {column: rules[rule](column) for column, rule in columns.items()}

    def set_column_config(self, target: str, config: dict) -> None:
        if target in self.columns_config.keys():
            if set(config.keys()) == set(self.columns_config[target]):
                self.columns_config[target] = config
            elif set(config.values()) == set(self.columns_config[target]):
                self.columns_config[target] = {v: k for k, v in config.items()}
            else:
                raise ValueError(f'''
                        Given items do not match with existing unique values of target column. 
                        Make sure you have included all of the existing unique values ({self.columns_config[target]}). 
                        Provided keys: {config.keys()}.
                        Provided values: {config.values()}
                    ''')
        else:
            raise ValueError(f'''
                    Given target column does not exist in the datasource. 
                    Make sure you use one of the listed columns {self.columns_config.keys()}
                ''')

