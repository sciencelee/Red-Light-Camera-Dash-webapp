from sodapy import Socrata
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go



# Create Socrata client
client = Socrata("data.cityofchicago.org", None)


def get_tinymap(latitude, longitude):
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
                         )
    print('violations data loaded')
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(red_cam)
    results_df['violations'] = results_df['violations'].astype(int)

    n_cams = len(results_df['camera_id'].unique())
    results_df['camera_id'] = results_df.camera_id.apply(lambda x: n_cams)
    results_df['violations'] = results_df['violations'].fillna(0)
    results_df['latitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['lat'])
    results_df['longitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['long'])

    #results_df['violation_date'] = pd.DatetimeIndex(results_df.violation_date).strftime("%Y-%m-%d")


    results_df = results_df.groupby(['violation_date', 'latitude', 'longitude']).agg({'violations':'sum'}).reset_index()
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
                            limit=10000,
                            )

    results_df = pd.DataFrame.from_records(crash_data)  # Convert to pandas DataFrame

    print('crash data loaded')
    results_df['crash_date'] = pd.DatetimeIndex(results_df.crash_date).strftime("%Y-%m-%d")
    #results_df['month'] = results_df.apply(lambda x: x.month)
    #results_df['year'] = results_df.apply(lambda x: x.year)
    results_df['injuries_total'] = results_df['injuries_total'].astype(int)
    results_df['injuries_incapacitating'] = results_df['injuries_incapacitating'].astype(int)

    results_df = results_df.groupby('crash_date').agg({'crash_record_id':'count', 'injuries_total':'sum', 'injuries_incapacitating':'sum'}).reset_index()



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

if __name__=='__main__':
    client = Socrata("data.cityofchicago.org", None)
    # test queries here
