from datetime import time
from dash.dcc.Slider import Slider
import pandas as pd
from dash import dcc, html
import dash
from load_data1 import Stockdatalocal
from dash.dependencies import Output, Input
import plotly_express as px
from time_filtering import filtertime
import dash_bootstrap_components as dbc



stock_data_object = Stockdatalocal()

symbol_dict = dict(AAPL = "Apple", TSLA = "Tesla", NVDA = "Nividia")

stock_options_dropdown = [{"label": name, "value": symbol}
                         for symbol, name in symbol_dict.items()]
df_dict = {symbol: stock_data_object.stock_dataframe(symbol)
            for symbol in symbol_dict}

#OHLC options = Open, High, Low, Close
ohlc_options = [{"label": option.capitalize , "value": option}
                for option in ["open", "high", "low", "close"]]

slider_marks = {i : mark for i,mark in enumerate(["1 day", "1 week", "1 month", "3 month", "1 year", "5 year", "Max"])}

stylesheets = [dbc.themes.MATERIA]
app = dash.Dash(__name__, external_stylesheets= stylesheets)

server = app.server 

app.layout = dbc.Container([

    dbc.Card([
        dbc.CardBody(html.H1("Stocky dashboard", className = "text-primary m-3"))
    ]),
    dbc.Row([
        dbc.Col(html.P("Choose a stock")),
        dbc.Col()
    ]),

    html.H1("Stocks viewer"),
    html.P("Choose a stock"),
    dcc.Dropdown(id='stock-picker-dropdown', className='',options = stock_options_dropdown,
    value = 'AAPL'
    ),
    html.P(id = "highest value"),
    html.P(id = "lowest value"),
    dcc.RadioItems(id='ohlc-radio', className='',
        options=ohlc_options,
        value='close'
    ),
    dcc.Graph(id='stock-graph', className = ''),
    dcc.Slider(id='time-slider', className = '',
    min = 0, max = 6, step = None, value = 2, marks = slider_marks),
    dcc.Store(id = "filtered-df")
    ])

@app.callback(Output("filtered-df", "data"),
            Input("stock-picker-dropdown", "value"),
            Input("time-slider","value"))
def filter_df(stock, time_index):
    """Filters the dataframe, stores intermediary for callbacks
    Returns:
    json object of filtered dataframe"""
    pass

    dff_daily , dff_intraday = df_dict[stock]

    dff = dff_intraday if time_index <= 2 else dff_daily

    
    days = {i: day for i, day in enumerate([1,7,30,90,365,365*5,])}
    dff = dff if time_index == 6 else filtertime(dff,days[time_index])

    return dff.to_json()


@app.callback(
    Output("stock-graph","figure"),
    Input("filtered-df", "data"),
    Input("stock-picker-dropdown", "value"),
    Input("ohlc-radio", "value")
)
def update_graph(json_df, stock, ohlc):

    dff = pd.read_json(json_df)
    fig = px.line(dff, x = dff.index, y = ohlc, title = "Hello")

    return fig #fig object goes into output property i.e figure property
@app.callback(
    Output("highest-value","children"),
    Output("lowest-value","children"),
    Input("filtered-df", "data"),
    Input("ohlc-radio","value")
)

def highest_lowest_value(json_df,ohlc):

    dff = pd.read_json(json_df)
    highest_value = f"High {dff[ohlc].max():.1f}"
    lowest_value = f"High {dff[ohlc].min():.1f}"
    return highest_value, lowest_value

if __name__ == "__main__":
    app.run_server(debug=True)