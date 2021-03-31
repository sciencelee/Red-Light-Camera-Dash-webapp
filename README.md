# Red Light Camera Dash Webapp
This web app is created to explore red light camera intersections in Chicago.  It plots daily violations, crashes, crash statistics, locations, and intersection characteristics in a beautiful and easy to use dashboard.  

# Description
The web app is live at: http://rlc.sciencelee.com
This is a companion web app for ![my red light camera project](https://github.com/sciencelee/chicago_rlc)

It is a single page Dash app.

<a href='http://rlc.sciencelee.com'>
  <img src='https://github.com/sciencelee/Red-Light-Camera-Dash-webapp/blob/master/assets/web_app_screenshot.png'></img>
</a>


### On the right side: 
- interactive map of all red light intersections in Chicago.
- Map colored by mean daily violations for selected interval
- radio button to select last 2yr, 1yr, or 6mos of data

### On the left side:
- basic statistics about selected intersection
- mapbox closeup of selected intersection
- daily violation plot of selected intersection over selected range
  - crashes are also included into plot (selected crash details included)
  - plot contains 5day moving average of violations

# Data 
All data is pulled from Chicago Data Portal website using Socrata queries using sodapy library
- crash data
- daily violation data

User created stats are also included. These are located in an imported py file and stored as dictionary. (anes, daily traffic etc.)
