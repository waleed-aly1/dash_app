import workdays
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_auth
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import warnings
import pandas as pd
from datetime import datetime, timedelta
import os

filename = 'XGB_Model_Predictions.csv'
lastmt = os.stat(filename).st_mtime
username_password_pairs = [['username', 'password']]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
auth = dash_auth.BasicAuth(app, username_password_pairs)

server = app.server

app.layout = html.Div([dbc.Tabs([
    dbc.Tab(html.Div([dash_table.DataTable(id='raw_data',
                                           data=[],
                                           style_table={
                                               'height': '200px',
                                               'overflowY': 'scroll',
                                           },
                                           style_cell={'textAlign': 'center',
                                                       'font_size': '11px',
                                                       'border': '1px solid black'
                                                       },
                                           style_header={'fontWeight': 'bold',
                                                         'font_size': '14px',
                                                         'color': 'white',
                                                         'backgroundColor': 'black'

                                                         },
                                           style_data_conditional=[
                                               {
                                                   'if': {'row_index': 'odd'},
                                                   'backgroundColor': 'rgb(248, 248, 248)',
                                               },
                                               {
                                                   'if': {'column_id': 'ModelDelta',
                                                          'filter_query': '{ModelDelta}<0'
                                                          },
                                                   'color': 'red',
                                               },
                                               {
                                                   'if': {'column_id': 'CLEDelta',
                                                          'filter_query': '{CLEDelta} < 0'
                                                          },
                                                   'color': 'red',
                                               },
                                               {
                                                   'if': {'column_id': 'PeriodDiff',
                                                          'filter_query': '{PeriodDiff}<0'
                                                          },
                                                   'color': 'red',
                                               },

                                           ]
                                           ),

                      dcc.Interval(id='interval_component',
                                   interval=600000,
                                   n_intervals=0
                                   )
                      ], style={'border-radius': '15px',
                                'box-shadow': '4px 4px 4px grey',
                                'background-color': '#f9f9f9',
                                'padding': '10px',
                                'margin-bottom': '10px',
                                'margin-left': '10px'

                                }
                     ), label='Actual Prices'),
    dbc.Tab(html.Div([dbc.Row([dbc.Col(dcc.Dropdown(id='diff_start_date_dropdown',
                                                    style={'font-size': '80%'},
                                                    placeholder='Start Point'
                                                    )),
                               dbc.Col(dcc.Dropdown(id='diff_end_date_dropdown',
                                                    style={'font-size': '80%'},
                                                    placeholder='End Point'
                                                    ))
                               ]),
                      dash_table.DataTable(id='differences',
                                           data=[],
                                           style_table={
                                               'height': '125px',
                                               'overflowY': 'scroll',
                                           },
                                           style_cell={'textAlign': 'center',
                                                       'font_size': '11px',
                                                       'border': '1px solid black'
                                                       },
                                           style_header={'fontWeight': 'bold',
                                                         'font_size': '14px',
                                                         'color': 'white',
                                                         'backgroundColor': 'black'

                                                         },
                                           style_data_conditional=[
                                               {
                                                   'if': {'row_index': 'odd'},
                                                   'backgroundColor': 'rgb(248, 248, 248)',
                                               },
                                               {
                                                   'if': {'row_index': 2},
                                                   'backgroundColor': 'lightyellow',
                                                   'fontWeight': 'bold'
                                               }
                                           ]
                                           ),

                      ], style={'border-radius': '15px',
                                'box-shadow': '4px 4px 4px grey',
                                'background-color': '#f9f9f9',
                                'padding': '10px',
                                'margin-bottom': '10px',
                                'margin-left': '10px'

                                }
                     ),
            label='Differences', id='tab2'
            )
], style={'font-size': '75%'}
),

    html.Div([
        dcc.Graph(id='delta_graph'),

    ], style={'width': '36%', 'display': 'inline-block',
              'border-radius': '15px',
              'box-shadow': '4px 4px 4px grey',
              'background-color': '#f9f9f9',
              'padding': '10px',
              'margin-bottom': '10px',
              'margin-left': '10px'

              }),

    html.Div([dcc.Graph(id='daily_running_graph'),

    ], style={'width': '36%', 'display': 'inline-block',
              'border-radius': '15px',
              'box-shadow': '4px 4px 4px grey',
              'background-color': '#f9f9f9',
              'padding': '10px',
              'margin-left': '100px',
              'margin-bottom': '10px'
              }),

    html.Div([
        dbc.Button('Refresh', id='refresh_button', n_clicks=0, size='sm', color='primary'),
        dcc.Dropdown(id='start_date_dropdown',
                     placeholder='Choose Start Date Override',
                     style={
                         'font-size': '90%',
                         'height': '40px',
                     }
                     )

    ], style={'margin': 'auto',
              'margin-bottom': '10px',
              'textAlign': 'center',
              'width': '220px'
              }
    ),
    html.Div([dcc.Graph(id='model_v_pred')],
             style={'border-radius': '15px',
                    'box-shadow': '4px 4px 4px grey',
                    'background-color': '#f9f9f9',
                    'padding': '10px',
                    'margin-bottom': '10px'})

])


# updates the main dropdown for the period chart and running daily total
@app.callback(Output('start_date_dropdown', 'options'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')
               ])
def update_dropdown_options(n_intervals, n_clicks):
    data = pd.read_csv(filename)

    dropdown_options = []
    for time in data['Timestamp']:
        dropdown_options.append({'label': time, 'value': time})
    dropdown_options.reverse()

    return dropdown_options


# dropdown for 2nd tab differencing
@app.callback(Output('diff_start_date_dropdown', 'options'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')
               ])
def diff_start_date_dropdown(n_intervals, n_clicks):
    data = pd.read_csv(filename)

    dropdown_options = []
    for time in data['Timestamp']:
        dropdown_options.append({'label': time, 'value': time})
    dropdown_options.reverse()
    return dropdown_options


# end date drop down
@app.callback(Output('diff_end_date_dropdown', 'options'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')
               ])
def diff_end_date_dropdown(n_intervals, n_clicks):
    data = pd.read_csv(filename)

    dropdown_options = []
    for time in data['Timestamp']:
        dropdown_options.append({'label': time, 'value': time})
    dropdown_options.reverse()

    return dropdown_options


# main data table rows
@app.callback(Output('raw_data', 'data'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')])
def update_rows(n_intervals, n_clicks):
    data = pd.read_csv(filename)

    data_sorted = data.sort_values('Timestamp', ascending=False)

    data_rounded = data_sorted.round(4)
    dict = data_rounded.to_dict('records')

    return dict


# main data table cols
@app.callback(Output('raw_data', 'columns'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')
               ])
def update_cols(n_intervals, n_clicks):
    data = pd.read_csv(filename)
    columns = [{'id': i, 'names': i} for i in data.columns]
    return columns


# differences table rows
@app.callback(Output('differences', 'data'),
              [Input('diff_start_date_dropdown', 'value'),
               Input('diff_end_date_dropdown', 'value')])
def updated_diff_table_rows(date1, date2):
    if date1 is None or date2 is None:
        return ''
    else:
        data = pd.read_csv(filename)

        # data_sorted = data.sort_values('Timestamp', ascending=False)
        data.set_index('Timestamp', inplace=True)
        data.loc['Difference'] = data.loc[date2] - data.loc[date1]
        data.reset_index(inplace=True)
        new_df = data[data['Timestamp'].isin([date1, date2, 'Difference'])]
        rounded_df = new_df.round(4)

        dict = rounded_df.to_dict('records')

        return dict


# difference data table cols
@app.callback(Output('differences', 'columns'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')
               ])
def update_cols(n_intervals, n_clicks):
    data = pd.read_csv(filename)
    columns = [{'id': i, 'names': i} for i in data.columns]
    return columns


@app.callback(Output('delta_graph', 'figure'),
              [Input('interval_component', 'n_intervals'),
               Input('start_date_dropdown', 'value'),
               Input('refresh_button', 'n_clicks')])
def update_period_graph(n_intervals, value, n_clicks):
    df = pd.read_csv(filename, index_col='Timestamp', parse_dates=True, infer_datetime_format=True)

    if value is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            start_day = workdays.workday(datetime.today(), -1)
            start_day_time = datetime(start_day.year, start_day.month, start_day.day, 17, 0)
            df_start = df.index.values[df.index.get_loc(start_day_time, method='nearest')]
    else:
        start = datetime.strptime(value.split('+')[0], '%Y-%m-%d %H:%M:%S')
        df_start = datetime(start.year, start.month, start.day, start.hour, start.minute, start.second)

    df_end = df.index.max()

    filtered_df = df.loc[df_start:df_end].copy()

    target_bar = go.Bar(x=filtered_df.index,
                        y=filtered_df['CLEDelta'],
                        name='CLE',
                        marker=dict(color='#FFD700')
                        )
    model_bar = go.Bar(x=filtered_df.index,
                       y=filtered_df['ModelDelta'],
                       name='Model',
                       marker=dict(color='#9EA0A1'))
    data = [target_bar, model_bar]
    layout = go.Layout(title='Period by Period Change',
                       titlefont={'size': 16,
                                  'family': 'Balto'},
                       xaxis={'type': 'category',
                              'dtick': 3,
                              'tickangle': 30,
                              'showline': True,
                              'ticks': 'inside',

                              'tickfont': {'family': 'PT Sans Narrpw',
                                           'size': 12
                                           }
                              },
                       yaxis={'showline': True}

                       )
    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(Output('daily_running_graph', 'figure'),
              [Input('interval_component', 'n_intervals'),
               Input('start_date_dropdown', 'value'),
               Input('refresh_button', 'n_clicks')])
def updated_running_daily_total(n_intervals, value, nclicks):
    data = pd.read_csv(filename, index_col='Timestamp', parse_dates=True, infer_datetime_format=True)

    if value is None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            start_day = workdays.workday(datetime.today(), -1)
            start_day_time = datetime(start_day.year, start_day.month, start_day.day, 17, 0, )
            df_start = data.index.values[data.index.get_loc(start_day_time, method='nearest')]
    else:
        start = datetime.strptime(value.split('+')[0], '%Y-%m-%d %H:%M:%S')
        df_start = datetime(start.year, start.month, start.day, start.hour, start.minute, start.second)

    df_end = data.index.max()

    filtered_df = data.loc[df_start:df_end].copy()
    filtered_df['ModelRunning'] = round(filtered_df['y_pred'] - filtered_df.loc[df_start]['y_pred'], 2)
    filtered_df['CrudeRunning'] = round(filtered_df['CLE'] - filtered_df.loc[df_start]['CLE'], 2)
    filtered_df['RunningDailyTotal'] = filtered_df['ModelRunning'] - filtered_df['CrudeRunning']
    latest_value = round(filtered_df.loc[df_end]['RunningDailyTotal'], 2)

    data = [go.Scatter(x=filtered_df.index,
                       y=filtered_df['RunningDailyTotal'],
                       mode='lines',
                       marker={'color': 'lightblue'}
                       )
            ]
    layout = go.Layout(title='Running Daily Total:{} '.format(latest_value),
                       titlefont={'size': 16,
                                  'family': 'Balto'},
                       xaxis={'showspikes': True,
                              'spikemode': 'toaxis'

                              }

                       )
    return go.Figure(data=data, layout=layout)


@app.callback(Output('model_v_pred', 'figure'),
              [Input('interval_component', 'n_intervals'),
               Input('refresh_button', 'n_clicks')])
def update_running_graph(n_intervals, nclicks):
    df = pd.read_csv(filename)
    new_df = df['Timestamp'].str.split('+', expand=True)
    df['Timestamp'] = new_df[0]
    latest_value = round(df['ModelDiff'].iloc[-1], 2)

    trace1 = go.Scatter(x=df['Timestamp'],
                        y=df['CLE'],
                        name='Crude',
                        mode='lines',
                        marker={'color': '#FFD700'},
                        yaxis='y2'
                        )

    trace2 = go.Scatter(x=df['Timestamp'],
                        y=df['y_pred'],
                        name='Model',
                        mode='lines',
                        marker={'color': '#9EA0A1'},
                        yaxis='y2'
                        )

    trace3 = go.Bar(x=df['Timestamp'],
                    y=df['ModelDiff'],
                    name='Diff',
                    marker={'color': 'lightblue'}

                    )

    data = [trace1, trace2, trace3]
    layout = go.Layout(title='Crude vs Model: {}'.format(latest_value),
                       titlefont={'size': 16,
                                  'family': 'Balto'},
                       yaxis=dict(domain=[0, .25],
                                  ),
                       yaxis2=dict(domain=[.27, 1],
                                   ),
                       margin=dict(t=80),
                       legend={'orientation': 'v'},
                       xaxis={'type': 'category',
                              'nticks': 15,
                              'tickangle': 30,
                              'showspikes': True,
                              'spikethickness': 2,
                              'spikemode': "toaxis+across+marker",
                              'ticks': 'outside',
                              'showgrid': True,
                              'tickfont': {'family': 'PT Sans Narrpw',
                                           'size': 12
                                           }

                              }

                       )

    return go.Figure(data=data, layout=layout)


if __name__ == '__main__':
    app.run_server()
