from sodapy import Socrata
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



# Create Socrata client
client = Socrata("data.cityofchicago.org", None)

def stats_table(annual_violations, crashes, int_df, intersection):
    print(int_df.columns)
    daily_mean = annual_violations['violations'].sum() / 365
    total_crashes = crashes['crash_record_id'].count()
    total_injuries = crashes['injuries_total'].sum()
    total_incap = crashes['injuries_incapacitating'].sum()
    lanes = int_df[int_df['intersection'] == intersection]['total_lanes'].values[0]
    daily_volume = int_df[int_df['intersection'] == intersection]['daily_traffic'].values[0]
    ways = int_df[int_df['intersection'] == intersection]['way'].values[0]
    n_cams = annual_violations['n_cams'].min()
    table1 = html.Table([
                    html.Tr('Mean Daily Violations: {:.1f}'.format(daily_mean)),
                    html.Tr('Revenue: ${:,}'.format(annual_violations['violations'].sum() * 100)),
                    html.Tr('Crashes: {}'.format(total_crashes)),
                    html.Tr('Injuries: {}'.format(total_injuries)),
                    html.Tr('Incapacitating Injuries: {}'.format(total_incap)),],
                    className='table-flex'
                     )

    table2 = html.Table([
                        html.Tr('Daily Volume: {:,}'.format(daily_volume)),
                        html.Tr('Total Lanes: {}'.format(lanes)),
                        html.Tr('Ways: {}'.format(ways)),
                        html.Tr('N Cameras: {}'.format(n_cams))
                        ], className='table-flex'
                        )

    return table1, table2


def get_tinymap(int_df, intersection):
    # make the tiny map
    latitude = int_df[int_df['intersection'] == intersection]['lat'].values[0]
    longitude = int_df[int_df['intersection'] == intersection]['long'].values[0]
    print('tinymap', latitude, longitude)
    fig = px.scatter_mapbox(lat=[latitude],
                            lon=[longitude],
                            zoom=16,
                            center=dict(
                                lat=latitude,
                                lon=longitude,
                            )
                            )

    fig.update_layout(mapbox_style="open-street-map",
                      margin=go.layout.Margin(l=0,  # left margin
                                              r=0,  # right margin
                                              b=0,  # bottom margin
                                              t=0,  # top margin
                                              ),
                      )
    return fig

def get_violations(intersection, start_date, today_str, int_chars):
    # load my violations data and preprocess
    # returned as JSON from API / converted to Python list of ictionaries by sodapy.

    # red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
    #                        where="violation_date BETWEEN '{}' AND '{}'".format(start_date, today_str),
    #                        limit=1000000,
    #                        )

    red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
                         select='intersection, violations, violation_date, camera_id',
                         where='''violation_date BETWEEN "{}" AND "{}"
                                    AND intersection = "{}"'''.format(start_date, today_str, intersection),
                         order='violation_date',
                         limit=1000000,
                         )
    print('violations data loaded')

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(red_cam)

    results_df['violations'] = results_df['violations'].astype(int)
    results_df['violations'] = results_df['violations'].fillna(0)

    n_cams = len(results_df['camera_id'].unique())
    print("NCAMS", n_cams)

    results_df['n_cams'] = results_df.camera_id.apply(lambda x: n_cams)
    results_df['latitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['lat'])
    results_df['longitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['long'])

    results_df['violation_date'] = pd.DatetimeIndex(results_df.violation_date).strftime("%Y-%m-%d")


    results_df = results_df.groupby(['violation_date', 'latitude', 'longitude', 'n_cams']).agg({'violations':'sum'}).reset_index()
    results_df['MA5'] = results_df.violations.rolling(5).mean()
    results_df['date'] = pd.to_datetime(results_df['violation_date'])
    results_df['weekday'] = results_df['date'].apply(lambda x: x.strftime('%A'))

    #results_df['violation_date'] = pd.to_datetime(results_df['violation_date'])
    #results_df['month'] = results_df['violation_date'].apply(lambda x: x.month)
    #results_df['weekday'] = results_df['violation_date'].apply(lambda x: datetime.weekday(x))
    #results_df['year'] = results_df['violation_date'].apply(lambda x: x.year)
    return results_df

def get_crashes(intersection, start_date, today_str, int_chars):
    # load my violations data and preprocess
    # returned as JSON from API / converted to Python list of ictionaries by sodapy.
    box_side = 100  # effectively makes it check for crash being within 40m of intersection
    box_lat = box_side / 111070 / 2  # 111070 is meters in deg lat in Chicago
    box_long = box_side / 83000 / 2  # 83000 is meters in deg long in Chicago

    crash_data = client.get("85ca-t3if",
                            select='*',
                            where='''crash_date BETWEEN "{}" AND "{}"
                                    AND latitude BETWEEN {} AND {}
                                    AND longitude BETWEEN {} AND {} 
                                    AND traffic_control_device = "TRAFFIC SIGNAL"
                                    AND intersection_related_i = "Y"
                                    '''.format(start_date,
                                               today_str,
                                               int_chars[intersection]['lat'] - box_lat,
                                               int_chars[intersection]['lat'] + box_lat,
                                               int_chars[intersection]['long'] - box_long,
                                               int_chars[intersection]['long'] + box_long,
                                               ),
                            limit=100000,
                            )

    results_df = pd.DataFrame.from_records(crash_data)  # Convert to pandas DataFrame

    print('crash data loaded')
    #results_df['crash_date'] = pd.DatetimeIndex(results_df.crash_date).strftime("%Y-%m-%d")
    #results_df['month'] = results_df.apply(lambda x: x.month)
    #results_df['year'] = results_df.apply(lambda x: x.year)
    results_df['injuries_total'] = results_df['injuries_total'].astype(int)
    results_df['injuries_incapacitating'] = results_df['injuries_incapacitating'].astype(int)

    #results_df['first_crash_type'] = results_df.groupby('crash_date', as_index=False)[['first_crash_type']].aggregate(lambda x: list(x)))


    results_df = results_df.groupby('crash_date').agg({'crash_record_id':'count',
                                                       'injuries_total':'sum',
                                                       'injuries_incapacitating':'sum',
                                                       'first_crash_type': lambda x: list(x),
                                                       'weather_condition': lambda x: list(x),
                                                       'lighting_condition': lambda x: list(x),
                                                       'damage': lambda x: list(x),
                                                       }).reset_index()

    #results_df['violation_date'] = pd.to_datetime(results_df['violation_date'])
    #results_df['month'] = results_df['violation_date'].apply(lambda x: x.month)
    #results_df['weekday'] = results_df['violation_date'].apply(lambda x: datetime.weekday(x))
    #results_df['year'] = results_df['violation_date'].apply(lambda x: x.year)
    return results_df



def cams_to_intersections(cams_df, int_chars):
    cams_df['latitude'] = cams_df['intersection'].apply(lambda x: int_chars[x]['lat'])
    cams_df['longitude'] = cams_df['intersection']

# Functions to grab our datasets
def load_map_cams(start_date, today_str):
    # load my violations data and preprocess
    # returned as JSON from API / converted to Python list of ictionaries by sodapy.

    # red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
    #                        where="violation_date BETWEEN '{}' AND '{}'".format(start_date, today_str),
    #                        limit=1000000,
    #                        )

    red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
                         select='intersection, SUM(violations) as violations',
                         group= 'intersection',
                         where='''violation_date BETWEEN "{}" AND "{}"'''.format(start_date, today_str),)
    print('red cam data loaded')
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(red_cam)
    results_df['violations'] = results_df['violations'].astype(int)
    return results_df

# Functions to grab our datasets
def load_hourly_cams(start_date, today_str):
    # load my violations data and preprocess
    # returned as JSON from API / converted to Python list of ictionaries by sodapy.

    # red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
    #                        where="violation_date BETWEEN '{}' AND '{}'".format(start_date, today_str),
    #                        limit=1000000,
    #                        )

    red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
                         select='intersection, SUM(violations)',
                         group= 'intersection' ,
                         where='''violation_date BETWEEN "{}" AND "{}"'''.format(start_date, today_str),)
    print('hourly cams loaded')
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(red_cam)
    results_df['violations'] = results_df['violations'].astype(int)
    results_df['latitude'] = results_df['latitude'].astype(float)
    results_df['longitude'] = results_df['longitude'].astype(float)
    results_df['violation_date'] = pd.to_datetime(results_df['violation_date'])
    results_df['month'] = results_df['violation_date'].apply(lambda x: x.month)
    results_df['weekday'] = results_df['violation_date'].apply(lambda x: datetime.weekday(x))
    results_df['year'] = results_df['violation_date'].apply(lambda x: x.year)
    return results_df



def load_crashes(start_date, today_str):
    # Crash Data
    crash_data = client.get("85ca-t3if",
                            where='''(crash_date BETWEEN '{}' AND '{}')
                               '''.format(start_date, today_str),

                            limit=1000000,
                            )
    print('crash data loaded')
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(crash_data)
    return results_df


def look_up_roads(road_list, daily_traffic):
    '''
    Look up function to get the values and return the total
            Parameters:
                roads (list): road segment list for intersection
            Returns:
                total (int): combined traffic volume of every road in roads list.
    '''
    total = 0
    for road in road_list:
        count = daily_traffic[daily_traffic['traffic_volume_count_location_address']==road]['total_passing_vehicle_volume'].values[0]
        total += int(count)
    return total




def add_traffic(int_df):
    daily_traffic = client.get("pfsx-4n4m",
                               limit=2000,
                               )

    daily_traffic = pd.DataFrame.from_records(daily_traffic)  # Convert to pandas DataFrame
    int_df['daily_traffic'] = int_df['roads'].apply(lambda x: look_up_roads(x, daily_traffic))

    return int_df


if __name__=='__main__':
    client = Socrata("data.cityofchicago.org", None)
    # test queries here
