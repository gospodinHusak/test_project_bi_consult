from components import DataSource


movements = DataSource(
    'Movements.csv', sep=';', filter_columns={'Date': 'minmax'},
    set_date_columns={'Date': '%d.%m.%Y'}
)


items = DataSource(
    'Items.csv', sep=';', filter_columns={'Name': 'unique'}
)