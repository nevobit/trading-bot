import dash
from dash import html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from classes import Bot
import time

timeframes = ['D1', 'H4', 'H1', 'M15', 'M5', 'M1']

bot1 = Bot("EURUSD",0.01,30,4,"buy", timeframes)
bot2 = Bot("GBPUSD",0.01,30,4,"buy", timeframes)

# Creamos una lista para almacenar las entradas diarias y las transacciones
daily_entries = []
transactions = []

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Trading"),

    html.Div([
        html.Div([
            html.H2("Entradas Diarias"),
            dash_table.DataTable(
                id='daily-entries',
                columns=[{'name': i, 'id': i} for i in daily_entries]
            )
        ], className="six columns"),

        html.Div([
            html.H2("Transacciones"),
            dash_table.DataTable(
                id='transactions',
                columns=[{'name': i, 'id': i} for i in transactions]
            )
        ], className="six columns")
    ])
])

# Callback para actualizar las entradas diarias y transacciones
@app.callback(
    [Output('daily-entries', 'data'),
     Output('transactions', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    # Lógica para actualizar las entradas diarias y transacciones
    # Puedes obtener esta información de tu bot o de algún otro origen de datos
    
    # Aquí vamos a usar el bot para obtener los datos actualizados
    bot1.run()
    bot2.run()

    # Obtener datos de las entradas diarias y transacciones del bot
    # Suponiendo que el bot tiene atributos daily_entries y transactions
    daily_entries_data = bot1.daily_entries
    transactions_data = bot1.transactions + bot2.transactions

    return daily_entries_data, transactions_data

if __name__ == '__main__':
    app.run_server(debug=True)
