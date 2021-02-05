# Dash app to support EDA on Chicago Red Light Camera study
# by Aaron Lee

import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#import plotly.express as px
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
import timeit
from assets.myfuncs import *
from assets.int_chars import *
#import plotly.graph_objects as go


# load my intersection data
int_chars.keys()
int_df = pd.DataFrame.from_dict(int_chars, orient='index')
int_df['intersection'] = int_chars.keys()



# would like to time this.  I only have 30s to load first time
# my_time = timeit.Timer()


today=datetime.today()
one_mos_ago = today - relativedelta(month=1) # for testing
one_mos_ago = "{}-{}-{}T00:00:00.000".format(one_mos_ago.year, one_mos_ago.month, one_mos_ago.day)

six_mos_ago = today - relativedelta(month=6)
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
                        width=600,
                        custom_data=['intersection', 'violations'],  #send in what you like this way (behind the scenes, sneaky!)
                        size='size',
                        hover_data={'size':False, 'intersection':True, 'violations': True, 'longitude': ':.3f', 'latitude': ':.3f'},
                        size_max=8,
                        )

fig.update_layout(mapbox_style="carto-positron",
                  margin=go.layout.Margin(l=0, #left margin
                                            r=0, #right margin
                                            b=0, #bottom margin
                                            t=0, #top margin
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
                    html.H3(id='title', children="Chicago Red Light Camera Accident Study (Aaron Lee 2021)"),
                    html.Div([   # Big middle block split in two
                        html.Div([  # This is my left half div
                                html.H3(id='stats', children="select a red light camera from map"),

                                ], className="flex-child left"),
                        html.Div([
                                html.Div(
                                    dcc.Dropdown(  # dropdown selector for my map.  Might remove this
                                            id='mapstyle-val',
                                            className='select columns',
                                            options=[
                                                    {'label': 'Stamen-toner', 'value': 'stamen-toner'},
                                                    {'label': 'Open-street-map', 'value': 'open-street-map'},
                                                    {'label': 'Carto-positron', 'value': 'carto-positron'},
                                                    {'label': 'Stamen-watercolor', 'value': "stamen-watercolor"},
                                                    ],
                                            value="stamen-toner",
                                            ),
                                        ),
                                html.Div(  # this is my div that contains my map.  look to css to change size etc.
                                        dcc.Graph(id='map', figure=fig),
                                        className='my-graph'
                                        )

                                ], className="flex-child right",
                                ),
                            ], className='flex-container'),
                        ],
            style = {'height': '100vh'},
            )


# use rows here so we have display above, and footer below.


#    html.Div([html.H3('Aaron Lee: (c)2020')]) # same level as big div




# THIS IS A CALLBACK TO UPDATE THE MAP BACKGROUND (MY FIRST ATTEMPT IN DASH)
# @app.callback(
#     Output('map', 'figure'),  # output goes to id:map and attribute:figure (which is my fig map)
#     Input('mapstyle-val', 'value'))  # mapstyle-val is my button label, value is the selection
# def update_style(value):
#     '''
#     My first callback with Dash.
#     callback (INPUT) triggers this function
#     function returns to the output location (in this case the Graph figure
#     '''
#     fig.update_layout(mapbox_style=value)  # change the map style and kick it back
#     return fig



# THIS CALLBACK UPDATES THE MAP WHEN YOU CLICK AN INTERSECTION
@app.callback(Output('stats', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
                Input('map', 'clickData')) # mapstyle-val is my button label, value is the data of teh item clicked
def update_map(clickData):
    '''
    My second callback with Dash. Yay!
    callback (INPUT) triggers this function
    function returns to the output location (in this case the Graph figure
    '''
    if not clickData:
        return dash.no_update
    intersection = clickData['points'][0]['customdata'][0]
    print(intersection)

    annual_violations = get_violations(intersection, year_ago_today, today_str, int_chars)  # Sql query funcs go here
    crashes = get_crashes(intersection, year_ago_today, today_str, int_chars)

    # stats for violations
    daily_mean = annual_violations['violations'].sum()/365


    # stats for crashes
    total_crashes = crashes['crash_record_id'].count()
    total_injuries = crashes['injuries_total'].sum()
    total_incap = crashes['injuries_incapacitating'].sum()

    # make violations graph
    new_fig = px.bar(annual_violations,
                     x='violation_date',
                     y='violations',
                     title='Daily Violations: {}'.format(intersection.upper()),
                     height=500,
                     hover_data=['weekday'],
                     )

    new_fig.add_trace(go.Scatter(x=annual_violations['violation_date'],
                                 y=annual_violations['MA5'],
                                 mode='lines',
                                 name='5 day moving avg.',
                                 line_color='red',))

    # make crash graph

    new_fig.add_trace(go.Scatter(x=crashes['crash_date'],
                                y=crashes['crash_record_id'],
                                 mode='markers',
                                 name='Crashes',
                                 marker=dict(
                                     color='cyan',
                                     size=10,
                                     line=dict(
                                         color='black',
                                         width=1
                                     )
                                 ),
                                 )
                      )


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

    # make the tiny map
    lat = int_df[int_df['intersection'] == intersection]['lat'].values[0]
    long = int_df[int_df['intersection'] == intersection]['long'].values[0]

    print("LAT???", type(lat))
    tinymap = get_tinymap(lat, long)

    #new_fig.update_traces

    # Now return my div containing my graph (dcc.Graph) along with my table data
    return html.Div([
                    html.Div([

                        html.Table([
                                    html.Tr([html.Td('{}'.format(intersection.upper()))]),
                                    html.Tr('Mean Daily Violations: {:.2f}'.format(daily_mean)),
                                    html.Tr('Annual Revenue (est): ${:,}'.format(annual_violations['violations'].sum()*100)),
                                    html.Tr('Crashes: {}'.format(total_crashes)),
                                    html.Tr('Injuries: {}'.format(total_injuries)),
                                    html.Tr('Incapacitating Injuries: {}'.format(total_incap)),
                                    ], className='table-flex'
                                    ),

                        html.Table([
                                    html.Tr([html.Td('{}'.format(intersection.upper()))]),
                                    html.Tr('Mean Daily Violations: {:.2f}'.format(daily_mean)),
                                    html.Tr('Annual Revenue (est): ${:,}'.format(annual_violations['violations'].sum() * 100)),
                                    html.Tr('Crashes: {}'.format(total_crashes)),
                                    html.Tr('Injuries: {}'.format(total_injuries)),
                                    html.Tr('Incapacitating Injuries: {}'.format(total_incap)),
                                    ], className='table-flex'
                                    ),

                        dcc.Graph(figure=tinymap, className='tiny-map flex-child')
                        ],
                        className='stats-table table-container'
                    ),
                    dcc.Graph(figure=new_fig, className='my-graph violations')]
                    ,
                    )


if __name__ == '__main__':
    app.run_server(debug=False)
