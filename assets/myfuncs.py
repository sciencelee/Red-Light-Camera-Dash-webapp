from sodapy import Socrata
import pandas as pd
from datetime import datetime



# Create Socrata client
client = Socrata("data.cityofchicago.org", None)



def get_violations(intersection, start_date, today_str, int_chars):
    # load my violations data and preprocess
    # returned as JSON from API / converted to Python list of ictionaries by sodapy.

    # red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
    #                        where="violation_date BETWEEN '{}' AND '{}'".format(start_date, today_str),
    #                        limit=1000000,
    #                        )

    red_cam = client.get("spqx-js37",  # speed cams are at 'hhkd-xvj4'
                         select='intersection, violations, violation_date',
                         where='''violation_date BETWEEN "{}" AND "{}"
                                    AND intersection = "{}"'''.format(start_date, today_str, intersection),
                         order='violation_date',
                         )
    print('violations data loaded')
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(red_cam)
    results_df['violations'] = results_df['violations'].astype(int)
    results_df['latitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['lat'])
    results_df['longitude'] = results_df['intersection'].apply(lambda x: int_chars[x]['long'])
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
