# Dash app to support EDA on Chicago Red Light Camera study
# by Aaron Lee

import json
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sodapy import Socrata
from datetime import datetime
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta


# get my data
# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofchicago.org", None)

# First 'limit' results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
today=datetime.today()
two_year_ago_today = year_ago_today = "{}-{}-{}T00:00:00.000".format(today.year - 2, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",
year_ago_today = "{}-{}-{}T00:00:00.000".format(today.year - 1, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",
today_str = "{}-{}-{}T00:00:00.000".format(today.year, today.month, today.day)  #"violation_date": "2014-07-01T00:00:00.000",

# THIS IS WHERE WE GRAB OUR DATASET
red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
                       where="violation_date BETWEEN '{}' AND '{}'".format(year_ago_today, today_str),
                       limit=5000,
                       )

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(red_cam)

results_df['violations'] = results_df['violations'].apply(int)
results_df['latitude'] = results_df['latitude'].apply(float)
results_df['longitude'] = results_df['longitude'].apply(float)
results_df['violation_date'] = pd.to_datetime(results_df['violation_date'])
results_df['month'] = results_df['violation_date'].apply(lambda x: x.month)
results_df['weekday'] = results_df['violation_date'].apply(lambda x: datetime.weekday(x))
results_df['year'] = results_df['violation_date'].apply(lambda x: x.year)


df_plot = results_df.groupby(['camera_id'])['violations'].sum().reset_index()

df_plot['latitude'] = df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['latitude'].mode())
print('lat')
df_plot['longitude'] = df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['longitude'].mode())
print('long')
df_plot['intersection']= df_plot['camera_id'].apply(lambda x: results_df[results_df['camera_id']==x]['intersection'].mode())
print('intersection')

# fig = px.scatter_geo(results_df.groupby('camera_id').sum(), locations="iso_alpha",
#                      color="violations", # which column to use to set the color of markers
#                      #hover_name="country", # column added to hover information
#                      size="violations", # size of markers
#                      projection="natural earth")

# px.scatter_mapbox?
fig = px.scatter_mapbox(df_plot,
                        lat="latitude",
                        lon="longitude",
                        color='violations',
                        hover_name='intersection',
                        # label=['lat','long','violations'],
                        color_continuous_scale='rdylgn_r',
                        range_color=[df_plot['violations'].quantile(0.2), df_plot['violations'].quantile(0.8)],
                        # center={'lat':41.975605, 'lon': -87.731670},
                        zoom=9.5,
                        opacity=0.6,
                        height=700,
                        custom_data=['camera_id'],  #send in what you like this way (behind the scenes, sneaky!)
                        hover_data={'camera_id':True, 'violations': True, 'longitude': ':.3f', 'latitude': ':.3f'},
                        )

fig.update_layout(mapbox_style="stamen-toner")

# month plot
df_month = results_df.groupby(['month'])['violations'].sum().reset_index()
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months_fig = px.bar(df_month, x='month', y='violations')

# .update_layout(
#     xaxis = dict(
#         tickmode = 'array',
#         tickvals = [x for x in range(12)],
#         ticktext = months
#     )
# )


# Weekday plot
df_weekday = results_df.groupby(['weekday'])['violations'].sum().reset_index()
weekdays = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
weekday_fig = px.bar(df_weekday, x='weekday', y='violations')

# .update_layout(
#     xaxis = dict(
#         tickmode = 'array',
#         tickvals = [x for x in range(7)],
#         ticktext = weekdays
#     )
# )


fig_sub = make_subplots(rows=2, cols=1, shared_xaxes=False)
bar1 = months_fig['data'][0]
bar2 = weekday_fig['data'][0]


fig_sub.update_layout(height=600, title_text="Top Bottom Subplots")
fig_sub.add_trace(bar1, row=1, col=1)
fig_sub.add_trace(bar2, row=2, col=1)


# FUNCTIONS
def generate_table(dataframe, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # default styling from tutorials
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__)






app.layout = html.Div([
        html.Div([

        html.Div([
            html.H3(id='title1', children="select a red light camera from map"),
            #dcc.Graph(id='stats', figure=fig_sub),

        ], className="six columns"),

        html.Div([
                #html.Label('Map Style'),
                html.Div(
                    dcc.Dropdown(
                            id='mapstyle-val',
                            className='select columns',
                            options=[
                                    {'label': 'Stamen-toner', 'value': 'stamen-toner'},
                                    {'label': 'Open-street-map', 'value': 'open-street-map'},
                                    {'label': 'Carto-positron', 'value': 'carto-positron'},

                                    ],
                            value='stamen-toner'
                            ),
                        className='div-for-dropdown'),
                html.Div(
                        dcc.Graph(id='map', figure=fig),
                        className='my-graph'
                )
                ], className="six columns"),
        ], className="row"),
    html.Div([html.H3('Aaron Lee: (c)2020')]),
], style={}
)


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


@app.callback(Output('title1', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
                Input('map', 'clickData'))  # mapstyle-val is my button label, value is the data of teh item clicked
def update_map(clickData):
    '''
    My second callback with Dash. Yay!
    callback (INPUT) triggers this function
    function returns to the output location (in this case the Graph figure
    '''
    if not clickData:
        return dash.no_update
    cam_id = clickData['points'][0]['customdata'][0]
    print(cam_id)
    cam_df = results_df[results_df['camera_id']==cam_id]
    print(len(cam_df))
    #cam_df['intersection'] = cam_df['intersection'].apply(lambda x: cam_df['intersection'][0].title())


    # stats
    intersection = cam_df['intersection'].iloc[0]
    daily_mean = cam_df['violations'].mean()
    year_ago = datetime.today() - relativedelta(years=1)
    print(year_ago.date())
    #cam_df['violation_date'] = cam_df['violation_date'].apply(lambda x: x.date())
    annual_violations = cam_df[cam_df['violation_date'] >= year_ago]['violations'].sum()
    # graph
    df_new = cam_df.groupby('violation_date')['violations'].sum().reset_index()

    #weekdays = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
    #df_new['weekday'] = cam_df['weekday'].apply(lambda x: weekdays[x])
    # df_new['violation_date'] = df_new['violation_date'].apply(lambda x:  x.strftime("%m/%d/%Y"))
    #
    # base = datetime.today()
    # date_list = [base - datetime.timedelta(days=x) for x in range(365)]
    #
    # for date in date_list:
    #     if date not in df_new['violation_date']:
    #         df_new.append({'violation_date':date, 'violations':0})


    new_fig = px.bar(df_new, x='violation_date', y='violations')
    #new_fig.update_traces

    return html.Div([

                    html.Table([
                        html.Tr('Camera ID: {}'.format(cam_id)),
                        html.Tr('Intersection: {}'.format(intersection.title())),
                        html.Tr('Mean Daily Violations: {:.2f}'.format(daily_mean)),
                        html.Tr('Annual Revenue (est): ${:,}'.format(annual_violations*100)),]
                    ),
                    dcc.Graph(figure=new_fig, className='my-graph'),

                    ]
                    )


if __name__ == '__main__':
    app.run_server(debug=True)
