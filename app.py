# Dash app to support EDA on Chicago Red Light Camera study
# by Aaron Lee

import json
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
#import plotly.express as px
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
import timeit
from assets.myfuncs import *
from assets.int_chars import *
#import plotly.graph_objects as go
from datetime import date


# load my intersection data
int_chars.keys()
int_df = pd.DataFrame.from_dict(int_chars, orient='index')
int_df['intersection'] = int_chars.keys()
int_df = add_traffic(int_df)




# would like to time this.  I only have 30s to load first time
# my_time = timeit.Timer()


today=datetime.today()
one_mos_ago = today - relativedelta(month=1) # for testing
one_mos_ago = "{}-{}-{}T00:00:00.000".format(one_mos_ago.year, one_mos_ago.month, one_mos_ago.day)

six_mos_ago = today - relativedelta(180)
six_mos_ago = "{}-{}-{}T00:00:00.000".format(six_mos_ago.year, six_mos_ago.month, six_mos_ago.day)  #"violation_date": "2014-07-01T00:00:00.000",
#two_year_ago_today = "{}-{}-{}T00:00:00.000".format(today.year - 2, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",
year_ago_today = "{}-{}-{}T00:00:00.000".format(today.year - 1, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",

today_str = "{}-{}-{}T00:00:00.000".format(today.year, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",


# LOAD MY DATA
results_df = load_map_cams(one_mos_ago, today_str)
results_df['latitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['lat'])
results_df['longitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['long'])



#crash_df = load_crashes(one_mos_ago, today_str) # Convert to pandas DataFrame




df_plot = results_df[['intersection', 'violations', 'latitude', 'longitude']]
#df_plot = results_df.groupby(['camera_id'])['violations'].sum().reset_index()

# df_plot['latitude'] = df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['latitude'].mode())
# print('lat')
# df_plot['longitude'] = df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['longitude'].mode())
# print('long')
# df_plot['intersection']= df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['intersection'].mode())
# print('intersection')

# fig = px.scatter_geo(results_df.groupby('camera_id').sum(), locations="iso_alpha",
#                      color="violations", # which column to use to set the color of markers
#                      #hover_name="country", # column added to hover information
#                      size="violations", # size of markers
#                      projection="natural earth")

# px.scatter_mapbox?
df_plot['size']=df_plot['violations'].apply(lambda x: 8)

fig = px.scatter_mapbox(df_plot,
                        lat="latitude",
                        lon="longitude",
                        color='violations',
                        hover_name='intersection',
                        # label=['lat','long','violations'],
                        color_continuous_scale='rdylgn_r',
                        #color_continuous_scale='Plotly3',
                        range_color=[df_plot['violations'].quantile(0), df_plot['violations'].quantile(0.95)],
                        # center={'lat':41.975605, 'lon': -87.731670},
                        zoom=9.6,
                        opacity=0.8,
                        height=600,
                        custom_data=['intersection', 'violations'],  #send in what you like this way (behind the scenes, sneaky!)
                        size='size',
                        hover_data={'size':False, 'intersection':True, 'violations': True, 'longitude': ':.3f', 'latitude': ':.3f'},
                        size_max=8,
                        )

fig.update_layout(mapbox_style="carto-positron",
                  margin=go.layout.Margin(l=0, #left margin
                                            r=0, #right margin
                                            b=0, #bottom margin
                                            t=10, #top margin
                                            )
                  )



# month plot
#df_month = results_df.groupby(['month'])['violations'].sum().reset_index()
#months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#months_fig = px.bar(df_month, x='month', y='violations')

# .update_layout(
#     xaxis = dict(
#         tickmode = 'array',
#         tickvals = [x for x in range(12)],
#         ticktext = months
#     )
# )


# Weekday plot
#df_weekday = results_df.groupby(['weekday'])['violations'].sum().reset_index()
#weekdays = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
#weekday_fig = px.bar(df_weekday, x='weekday', y='violations')

# .update_layout(
#     xaxis = dict(
#         tickmode = 'array',
#         tickvals = [x for x in range(7)],
#         ticktext = weekdays
#     )
# )


#fig_sub = make_subplots(rows=2, cols=1, shared_xaxes=False)
#bar1 = months_fig['data'][0]
#bar2 = weekday_fig['data'][0]


#fig_sub.update_layout(height=600, title_text="Top Bottom Subplots")
#fig_sub.add_trace(bar1, row=1, col=1)
#fig_sub.add_trace(bar2, row=2, col=1)


# MY APP/WEBPAGE SPECIFIC FUNCTIONS
def generate_table(dataframe, max_rows=26):
    # generates an html table for my data display (left window)
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

# CREATE MY APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # default styling from tutorials
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# CREATE MY APP LAYOUT
# format is html.Tag([])   They are just lists of html elements to produce webpage nesting
app.layout = html.Div([  # one big div for page
                    html.Div(id='time-value', style={'display': 'none'}, children='one year'),  # place to store my time interval value
                    html.Div(id='intersection-value', style={'display': 'none'}, children='CICERO AND I55'), # place to store my intersection value

                    # Real page starts here
                    html.H3(id='title', children="Chicago Red Light Camera Accident Study"),
                    html.Div([   # Big middle block split in two
                        html.Div([  # This is my left half div
                                html.H3(id='stats', children="select a red light camera from map"),

                                ], className="flex-child left"),
                        html.Div([
                                    html.Div(  # this is my div that contains my map.  look to css to change size etc.
                                        dcc.Graph(id='map', figure=fig),
                                        className='my-graph'
                                        ),
                                     html.Div([
                                            dcc.Dropdown(  # dropdown selector for my map.  Might remove this
                                                    id='mapstyle-val',
                                                    className='select columns',
                                                    options=[
                                                            {'label': 'Stamen-toner', 'value': 'stamen-toner'},
                                                            {'label': 'Open-street-map', 'value': 'open-street-map'},
                                                            {'label': 'Carto-positron', 'value': 'carto-positron'},
                                                            ],
                                                    value="carto-positron",
                                                    ),

                                            dcc.RadioItems(  # dropdown selector for my map.  Might remove this
                                                    id='timeframe-val',
                                                    className='select columns',
                                                    options=[
                                                            {'label': 'Three Month', 'value': "3m"},
                                                            {'label': 'Six Months', 'value': "6m"},
                                                            {'label': 'One Year', 'value': '1y'},
                                                            {'label': 'Two Years', 'value': '2y'},
                                                            ],
                                                    value="1y",
                                                    ),
                                             html.H6("Aaron M. Lee {} 2021".format(u"\u00A9"))
                                            ], className='flex-container'),

                                ], className="flex-child right",
                                ),
                            ], className='flex-container'),
                        ],
            style = {'height': '100vh'},
            )


# use rows here so we have display above, and footer below.


#    html.Div([html.H3('Aaron Lee: (c)2020')]) # same level as big div






#THIS IS A CALLBACK TO UPDATE THE MAP BACKGROUND (MY FIRST ATTEMPT IN DASH)
@app.callback(
    Output('map', 'figure'),  # output goes to id:map and attribute:figure (which is my fig map)
    Input('mapstyle-val', 'value'))  # mapstyle-val is my button label, value is the selection
def update_style(value):
    '''
    My first callback with Dash.
    callback (INPUT) triggers this function
    function returns to the output location (in this case the Graph figure
    '''
    fig.update_layout(mapbox_style=value)  # change the map style and kick it back
    return fig


@app.callback(Output('intersection-value', 'children'),
              Input('map', 'clickData'))
def write_intersection(clickData):
     # write intersection to div
     if not clickData:
         return dash.no_update
     intersection = clickData['points'][0]['customdata'][0]
     print(intersection)
     return intersection


@app.callback(Output('time-value', 'children'),
              Input('timeframe-val', 'value'))
def write_time(value):
     # write intersection to div
     # if not value:
     #     return dash.no_update
     return value


# THIS CALLBACK UPDATES THE MAP WHEN YOU CLICK AN INTERSECTION oringal data commented out
# @app.callback(Output('stats', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
#                 Input('map', 'clickData')) # mapstyle-val is my button label, value is the data of teh item clicked
@app.callback(Output('stats', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
                Input('intersection-value', 'children'),  # mapstyle-val is my button label, value is the data of teh item clicked
                Input('time-value', 'children'))
def update_map(intersection, time_delta):
    '''
    My second callback with Dash. Yay!
    callback (INPUT) triggers this function
    function returns to the output location (in this case the Graph figure
    '''
    today = datetime.now()
    start_time = None

    if time_delta == '2y':
        start_time =  "{}-{}-{}T00:00:00.000".format(today.year - 2, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",
    elif time_delta == '1y':
        start_time =  "{}-{}-{}T00:00:00.000".format(today.year - 1, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",
    elif time_delta == '3m':
        three_mos_ago = today - relativedelta(months=3)
        start_time = "{}-{}-{}".format(three_mos_ago.year, three_mos_ago.month, three_mos_ago.day)
    elif time_delta == '6m':
        six_mos_ago = today - relativedelta(months=6)
        start_time = "{}-{}-{}".format(six_mos_ago.year, six_mos_ago.month, six_mos_ago.day)


    today_str = "{}-{}-{}T00:00:00.000".format(today.year, today.month, today.day)  # "violation_date": "2014-07-01T00:00:00.000",

    annual_violations = get_violations(intersection, start_time, today_str, int_chars)  # Sql query funcs go here
    crashes = get_crashes(intersection, start_time, today_str, int_chars)


    # make violations graph
    new_fig = px.bar(annual_violations,
                     x='violation_date',
                     y='violations',
                     #title='Daily Violations: {}'.format(intersection.upper()),
                     height=400,
                     hover_data=['weekday'],

                     )

    new_fig.add_trace(go.Scatter(x=annual_violations['violation_date'],
                                 y=annual_violations['MA5'],

                                 mode='lines',
                                 hoverinfo='skip',
                                 name='5 day moving avg.',
                                 line_color='red',))

    # make crash graph
    hover_list = ["Date: %{customdata[0]}",
                    "Crash Type: %{customdata[1]}",
                    "Injuries: %{customdata[2]}",
                    "Weather Cond: %{customdata[3]}",
                    "Damage: %{customdata[4]}"]

    new_fig.add_trace(go.Scatter(
                                x=crashes['crash_date'],
                                y=crashes['crash_record_id'],
                                mode='markers',
                                name='Crashes',
                                customdata=crashes[['crash_date', 'first_crash_type', 'injuries_total', 'weather_condition', 'damage']],
                                marker=dict(
                                    symbol='hexagram',

                                    color='gold',
                                     size=10,
                                     line=dict(
                                            color='red',
                                            width=1
                                              )
                                        ),
                                hovertemplate="<br>".join(hover_list)
                                        )
                      )
    #new_fig.update_traces(hovertemplate="<br>".join(hover_list))

    new_fig.update_layout(legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                orientation='h',
                font=dict(
                    family="Helvetica",
                    size=10,
                    color="black"
                        ),
                ),
            margin = go.layout.Margin(l=20,  # left margin
                                  r=20,  # right margin
                                  b=20,  # bottom margin
                                  t=30,  # top margin
                                  )
            )



    tinymap = get_tinymap(int_df, intersection)

    #new_fig.update_traces
    table1, table2 = stats_table(annual_violations, crashes, int_df, intersection)


    # Now return my div containing my graph (dcc.Graph) along with my table data
    # i made a diagram with numbered box model for this
    return html.Div([  # Big div on my left side

                    html.Div([ # div to contain grouping of intersection/title, stats-flextables, and tinymap flex 1
                            html.Div([  # 2 flex cont
                                    html.Div([  # 3 flex child
                                            html.H5(intersection),
                                            html.Div([ # 5 flex cont
                                                    html.Div(table1, className='flex-child'),  #6 flex child with table in it
                                                    html.Div(table2, className='flex-child')  #7 flex child with table in it
                                                    ], className='flex-container flex-child')
                                            ], className='flex-child flex2'),

                                    dcc.Graph(figure=tinymap, className='tinymap flex-child'), # 8
                                    ], className='flex-container')
                            ]),
                    dcc.Graph(figure=new_fig, className='my-graph violations'),
                    ])











        # html.H5(intersection),  # this should show on top
        #
        #                             html.Table([
        #                                         html.Tr('Mean Daily Violations: {:.2f}'.format(daily_mean)),
        #                                         html.Tr('Annual Revenue (est): ${:,}'.format(annual_violations['violations'].sum()*100)),
        #                                         html.Tr('Crashes: {}'.format(total_crashes)),
        #                                         html.Tr('Injuries: {}'.format(total_injuries)),
        #                                         html.Tr('Incapacitating Injuries: {}'.format(total_incap)),
        #                                         ], className='table-flex'
        #                                         ),
        #
        #                             html.Table([
        #                                         html.Tr('Daily Volume: {}'.format(1)),
        #                                         html.Tr('Total Lanes: {}'.format(lanes)),
        #                                         html.Tr('Ways: {}'.format(1)),
        #                                         ], className='table-flex'
        #                                         ),
        #                             ],
        #                         className='stats-flex table-container'
        #                             ),
        #                     ],
        #                     className='flex-container'
        #                     ),
        #             ])


if __name__ == '__main__':
    app.run_server(debug=False)
