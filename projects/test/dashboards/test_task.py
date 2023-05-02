import sys
import os
import inspect
sys.path.insert(1, os.path.dirname(os.path.split(inspect.stack()[0][1])[0]))
from datasources import *
from utils.funcs import *
from utils.constants import *

from components import Dashboard
import pandas as pd
from numpy import stack
import calendar
import plotly.graph_objects as go


overview = """
    Дашборд включает три окна, каждое из которых описано более подробно в справке, доступной по нажатии на соответствующую кнопку слева от окна. 
    Кроме того, на дашборде присутствует панель фильтров, которую можно открыть и закрыть нажатием на верхнюю правую кнопку. При взаимодействии 
    с фильтрами важно применить изменения, чтобы графики и таблица были актуальными.

    Крайне надеюсь, что функциональная и визуальная компоненты вам понравятся. Как я уже сказал, на домашней странице - это все еще W.I.P., 
    поскольку я в одиночку занимаюсь ее развитием. Здесь еще много что предстоит доработать: мне хочется доработать панель фильтров, чтобы фильтры 
    были синхронизированы между собой (т.е., например, если на календаре выбран диапазон, в который не попадает какая-то статья, она должна быть 
    отмечена как недоступная для пользовательского выбора), но тут много вопросов UX-овых, которые еще надо проработать. Еще хочется накинуть 
    анимацию на кнопку фильтров, когда панель открыта, чтобы оно как-то поестественнее выглядело. Меню дашбордов тоже надо переработать (откроется 
    при нажатии на 'Test Task'). Последние два пункта, конечно, мелочи, но тем не менее хочется, чтобы продукт был хорош везде.

    Много и других идей. Например, можно добавить к окнам кнопку 'открыть на весь экран'. Очень полезно бы было в случае, если нужно 
    сконцентрироваться на одном графике и как-то с ним поиграться. В эту же историю можно добавить кнопку ‘поменять визуализацию’. Конкретно в 
    данном случае можно было бы таблицу сменить на линейный график (просто как доп. опция)

    Важный момент, который не хочу упустить и не объяснить, поскольку он лежит в основе представленного прототипа. Я немного шаманил с данными и 
    помножил строки, когда тестил то, как вообще визуализации будут себя вести при изменениях. Если при данном объеме никаких проблем с 
    визуализациями нет, то когда у нас появится больше статей или больше исторических данных по ним, все начнет понемногу скукоживаться, пока не 
    станет совсем нечитаемым. Из-за профдеформации я не могу закрыть глаза, поэтому оба графика на дашборде зависят от строк таблицы. Сейчас все 
    строки выделены, данные полные, но можно снимать выделение строки в таблице, что отразится на визуализациях. К тому же у таблицы есть 
    ограничение в 10 строк на одну страницу. Если записей станет больше, то под таблицей появится функционал переключения страниц. Это и 
    выступает ограничителем, т.е. на визуализации будут попадать только статьи с текущей страницы. Не берусь сказать, насколько это удачное 
    решение. Будь это реальная задача, нужно было бы отталкиваться от цели дашборда: для чего он нужен заказчику? Хочет что-то сравнивать? 
    Хочет просто посмотреть на общие показатели, пролистывая таблицу?

    В итоге надеюсь, что данный дашборд в достаточной мере демонстрирует мои навыки работы со сложными дашбордами. Также буду рад обсудить любые 
    вопросы, которые у вас возникнут!
"""

dashboard = Dashboard(datasource_objs=[movements, items], overview_text=overview)

dashboard.add_filter(
    datasource_id='Movements',
    source_column='Date',
    filter_type='daterange',
)
dashboard.add_filter(
    datasource_id='Items',
    source_column='Name',
)

dashboard.add_parameter(
    name='Movement',
    options={'All': '', 'Expenses': "Movement < 0", 'Income': "Movement > 0"},
    default_value='',
)

dashboard.add_window(
    window_id=1,
    name='Summary table',
    row_start=1,
    row_end=2,
    col_start=1,
    col_end=2,
    content_type='table',
    info=(
        'Сводная таблица. Значениями является итоговое состояние "баланса" на конец месяца. У каждой строки есть '
        'чекбокс, отмеченный по умолчанию для текущей страницы. Выделенные статьи отрисовываются на остальных графиках'
    )
)

dashboard.add_window(
    window_id=2,
    name='Total Expenses and Earnings',
    row_start=1,
    row_end=2,
    col_start=2,
    col_end=4,
    content_type='graph',
    layout={},
    info=(
        'Барчарт, демонстрирующий суммарные доходы и расходы по каждой из статей'
    )
)

dashboard.add_window(
    window_id=3,
    name='Overall Amount Dynamics',
    row_start=2,
    row_end=2,
    col_start=1,
    col_end=4,
    content_type='graph',
    layout={},
    info=(
        'Линейный график, на котором, можно отследить динамику изменения баланса по каждой из статей. '
        'В отличие от таблицы, показывающей итог за месяц, здесь зафиксировано каждое изменение, что '
        'дает возможность проводить низкоуровневый анализ'
    )
)


def window_1(filterpanel_values):
    print('WINDOW 1')
    query_expressions = filterpanel_values['query_expressions']
    movement_param = filterpanel_values['parameters']['negative_positive']
    if movement_param != '':
        query_expressions['Movements'] += f' & {movement_param}'

    movement_df = movements.dataframe.query(query_expressions['Movements'])
    items_df = items.dataframe.query(query_expressions['Items'])
    movement_df['Date'] = pd.to_datetime(movement_df.Date, format='%Y-%m-%d')
    movement_df = (
        movement_df
        .sort_values(by=['Date', 'ID'])
        .groupby(['ID', pd.Grouper(key='Date', freq='1M')])['Movement']
        .sum()
        .groupby(level=0)
        .cumsum()
        .reset_index()
    )
    movement_df[['Year', 'Month']] = movement_df.Date.dt.to_period("M").astype('str').str.split('-', expand=True)
    movement_df['Month Name'] = movement_df['Month'].apply(lambda x: calendar.month_abbr[int(x)])
    merged_data = pd.merge(left=movement_df, right=items_df, how='inner', on='ID')
    pvt = merged_data.pivot_table(index='Name', columns=['Year', 'Month', 'Month Name'], values='Movement')
    pvt.columns = pvt.columns.droplevel(1)
    pvt = pvt.reset_index()
    columns, data = convert_df_to_dash(pvt)
    selected_rows = [i for i in range(len(pvt))]
    
    style_data_conditional = [
        {
            'if': {
                    'column_id': 'Name',
                    'filter_query': f'{{Name}} = "{name}"'
                },
                'color': color.format(opacity=1)
        }
        for name, color in NAME_COLORS.items()
    ]
    
    return [columns, data, selected_rows, style_data_conditional]


dashboard.set_callback(
    outputs={1: ['table.columns', 'table.data', 'table.selected_rows', 'table.style_data_conditional']},
    inputs={1: ['filterpanel_values_store.data']},
    func=window_1
)

def window_2(data, rows, filterpanel_values):
    names = [data[row]['Name'] for row in rows]

    query_expressions = filterpanel_values['query_expressions']
    movement_param = filterpanel_values['parameters']['negative_positive']
    if movement_param != '':
        query_expressions['Movements'] += f' & {movement_param}'

    movement_df = movements.dataframe.query(query_expressions['Movements'])
    items_df = items.dataframe.query(query_expressions['Items'])
    items_df = items_df.query(f'Name in {names}')

    movement_df = movement_df.groupby(['ID'])['Movement'].agg([('Spendings' , lambda x : (x[x < 0] * -1).sum()) , ('Earnings' , lambda x : x[x > 0].sum())])
    movement_df = movement_df.unstack().reset_index(name='Amount')
    movement_df.rename(columns={'level_0': 'Movement Type'}, inplace=True)

    merged_grpd = pd.merge(left=movement_df, right=items_df, how='inner', on='ID').sort_values(by='Name')
    
    fig_data = []
    
    for movement_type in sorted(merged_grpd['Movement Type'].unique()):
        trace_df = merged_grpd.query(f"`Movement Type` == '{movement_type}'")
        trace = go.Bar(
            x=trace_df.Name, 
            y=trace_df.Amount, 
            marker={
                'color': SPENDINGS_EARNINGS[movement_type].format(opacity=.1), 
                'line': {
                    'color': SPENDINGS_EARNINGS[movement_type].format(opacity=1), 
                    'width': 1.5
                }
            },
            text=trace_df.Amount,
            textfont={'color': "white"},
            textposition='auto',
            name=movement_type
        )
        fig_data.append(trace)

    fig = go.Figure(
    data=fig_data,
    layout={
        'hovermode': False,
        'barmode': 'group',
        'bargroupgap': .1,
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': {'b': 50, 'l': 0, 'r': 0, 't': 0},
        'xaxis': {
            'color': "white"
        },
        'yaxis': {
            'showgrid': False,
            'showline': False,
            'showticklabels': False,
            'zeroline': False,
        },
        'legend': {
            'orientation': "h",
            'y': -.05,
            'x': 1,
            'xanchor': 'right',
            'traceorder': "normal",
            'font': {'color': "white"}
        },
        'font': {'size': 16, 'family': 'Georgia, Serif'}
    }
)
    return fig

dashboard.set_callback(
    outputs={2: ['graph.figure']},
    inputs={
        1: ['table.data', 'table.selected_rows'],
        2: ['filterpanel_values_store.data']
    },
    func=window_2
)
    
def window_3(data, rows, filterpanel_values):
    names = [data[row]['Name'] for row in rows]
    
    query_expressions = filterpanel_values['query_expressions']
    movement_param = filterpanel_values['parameters']['negative_positive']
    if movement_param != '':
        query_expressions['Movements'] += f' & {movement_param}'

    movement_df = movements.dataframe.query(query_expressions['Movements'])
    items_df = items.dataframe.query(query_expressions['Items'])
    items_df = items_df.query(f'Name in {names}')
    movement_df['Date'] = pd.to_datetime(movement_df.Date, format='%Y-%m-%d')
    movement_df['Balance State'] = movement_df.sort_values(by=['Date', 'ID']).groupby(['ID'])['Movement'].cumsum()
    movement_df['Percent Change'] = round(movement_df.groupby(['ID'])['Balance State'].apply(pd.Series.pct_change) * 100, 1)
    merged_data = pd.merge(left=movement_df, right=items_df, how='inner', on='ID')
    
    fig_data = []
    
    for name in sorted(merged_data['Name'].unique()):
        trace_df = merged_data.query(f"Name == '{name}'")
        trace = go.Scatter(
            x=trace_df['Date'], 
            y=trace_df['Balance State'], 
            marker={'color': NAME_COLORS[name].format(opacity=1)},
            line={
                'color': NAME_COLORS[name].format(opacity=.8),
                'width': 1
            },
            mode='markers+lines+text',
            customdata=stack(([name for i in range(len(trace_df))], trace_df['Percent Change']), axis=-1),
            hoverinfo='x+y',
            hoverlabel_namelength=0,
            hovertemplate='<br>'.join(
                [
                    'Item: <b>%{customdata[0]}</b>',
                    'Date: <b>%{x}</b>', 
                    'Balance State: <b>%{y}</b>', 
                    'Percent Change: <b>%{customdata[1]}%</b>', 
                ]
            ),
            text=trace_df['Balance State'],
            textfont={'color': "white"},
            textposition='top center',
            name=name
        )
        fig_data.append(trace)

    fig = go.Figure(
        data=fig_data,
        layout={
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'b': 75, 'l': 0, 'r': 0, 't': 5},
            'xaxis': {
                'color': "white"
            },
            'yaxis': {
                'showgrid': False,
                'showline': False,
                'showticklabels': False,
                'zeroline': False,
                'range': [
                    merged_data.Movement.min() - 100, 
                    merged_data.Movement.max() + 100
                ]
            },
            'legend': {
                'orientation': "h",
                'x': 1,
                'y': -.12,
                'xanchor': 'right',
                'traceorder': "normal",
                'font': {'color': "white"}
            },
            'font': {'size': 16, 'family': 'Georgia, Serif'},
            'hoverlabel': {'font': {'family': 'Georgia, Serif', 'color': 'black'}}
        }
    )
    return fig

dashboard.set_callback(
    outputs={3: ['graph.figure']},
    inputs={
        1: ['table.data', 'table.selected_rows'],
        3: ['filterpanel_values_store.data']
    },
    func=window_3
)
