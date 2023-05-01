
EMPTY_LAYOUT = {
    'margin': {'b': 0, 'l': 0, 'r': 0, 't': 25},
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'xaxis': {
        'showgrid': False,
        'showline': False,
        'showticklabels': False,
        'zeroline': False
    },
    'yaxis': {
        'showgrid': False,
        'showline': False,
        'showticklabels': False,
        'zeroline': False,
    }
}

MODEBAR_BUTTONS = [
    'zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale', 'zoom2d', 'pan2d', 'select2d',
    'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'drawline', 'drawopenpath',
    'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape', 'zoom3d', 'pan3d', 'orbitRotation',
    'tableRotation', 'handleDrag3d', 'resetCameraDefault3d', 'resetCameraLastSave3d', 'hoverClosest3d',
    'hoverClosestCartesian', 'hoverCompareCartesian', 'zoomInGeo', 'zoomOutGeo', 'resetGeo', 'hoverClosestGeo',
    'hoverClosestGl2d', 'hoverClosestPie', 'toggleHover', 'resetViews', 'toImage', 'sendDataToCloud',
    'toggleSpikelines', 'resetViewMapbox'
]

META_BUTTONS = {
    'info': "ri:file-info-line",
    'data_table': "dashicons:editor-table"
}

DASHBOARDS_DIR = 'dashboards'

HOME_PAGE_TITLE = 'ANALYTIC PLATFORM'
ABOUT_TXT = (
    'Добро пожаловать на домашнюю страницу моей аналитической платформы, выполненную в стиле "веб-дизайн нулевых". '
    'На самом деле она сделана в данный момент исключительно для возможности разделить сгруппировать дашборды '
    'по конкретным проектам, не более того. В будущем, конечно, нужно будет переработать ее. Пока у меня недостаточно '
    'контента, чтобы полноценно заняться дизайном поэтому и это точно бэклог. Меню здесь собственно тоже максимально простое: '
    'жмете на интересующий проект (в данном случае Test), после чего выбираете ссылку на нужный дашборд (между '
    'дашбордами можно переключаться на странице дашборда, а вот чтобы сменить проект, надо вернуться на домашнуюю страницу)'
    'Надеюсь на понимаение с вашей стороны, поскольку в одиночку быстрыми темпами не удается развивать приложение при '
    'наличии других более срочных и важных задач.'
)

IGNORED = ['__pycache__']

TABLE_STYLE_CELL = {
    'padding': '5px',
    'backgroundColor': '#1f2326',
    'color': '#EBEBF5',
    'fontFamily': "TT Octosquares Condensed",
    'border': '1px solid #14141e'
}

TABLE_STYLE_HEADER = {
    'padding': '5px',
    'backgroundColor': '#1f2326',
    'color': '#ff4401',
    'fontWeight': 'bold',
    'fontFamily': "TT Octosquares Condensed",
    'border': '1px solid #14141e'
}