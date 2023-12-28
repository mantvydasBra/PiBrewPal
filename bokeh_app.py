from db import loadTemperature, getTempFreq
from bokeh.layouts import column, row, layout
from bokeh.plotting import figure, curdoc
from bokeh.models import DatetimeTickFormatter, HoverTool, WheelZoomTool, RangeTool, ColumnDataSource, Button, InlineStyleSheet, Spacer, CustomJS, Range1d
import pandas as pd
import requests
from time import sleep
import json

# Load temperature from database
df = loadTemperature()

# print(df)
# Create a Bokeh ColumnDataSource
source = ColumnDataSource(df)

# Global variable to hold the callback ID
current_callback_id = None
last_temp = 0


# Create a Bokeh figure
p = figure(
    title='Temperature Change Over Time', 
    x_axis_label='Timestamp', 
    y_axis_label='Temperature (°C)', 
    sizing_mode = "stretch_width", 
    height = 350,
    width = 800,
    x_axis_type = 'datetime',
    x_range = (df['MeasurementTime'].iloc[-5] - pd.Timedelta(seconds=5), df['MeasurementTime'].iloc[-1] + pd.Timedelta(seconds=5))
)
# Plot the line graph
line_renderer = p.line(
    x='MeasurementTime', 
    y='MeasuredValue', 
    source=source, 
    line_width=2
)
# Add dots to each data point
dots_renderer = p.circle(
    x='MeasurementTime', 
    y='MeasuredValue', 
    source=source, 
    size=8, 
    fill_color="white", 
    line_color="blue"
)
# Format the x-axis ticks as dates
p.xaxis.formatter=DatetimeTickFormatter(
    seconds = "%H:%M:%Ss",
    minsec = "%H:%M:%S",
    minutes = "%H:%Mh",
    hours="%H:%Mh",
    days="%B %d",
    months="%B %Y",
    years="%Y",
)
# Add a HoverTool to display information on hover
hover_tool = HoverTool(
    tooltips=[
        ('Timestamp', '@MeasurementTime{%Y-%m-%d %H:%M:%S}'),
        ('Temperature', '@MeasuredValue{0.0} °C'),
    ],
    formatters={'@MeasurementTime': 'datetime'},
    renderers=[dots_renderer],
)
p.add_tools(hover_tool)
# Enable wheel zoom by default
p.toolbar.active_scroll = p.select_one(WheelZoomTool)
# Create a graph for range_tool
select = figure(
    title="Drag the middle and edges of the selection box to change the range above",
    height=130, 
    width=800, 
    y_range=p.y_range,
    x_axis_type="datetime", 
    y_axis_type=None,
    tools="", 
    toolbar_location=None, 
    background_fill_color="#efefef"
)
# Formatter to make the dates look nicer
select.xaxis.formatter=DatetimeTickFormatter(
    days="%B %d",
    months="%B %Y",
    years="%Y",
)
# Create rangetool, x_range will get the coordinates from p graph
range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2
# Draw a line graph on select object
select.line(
    x="MeasurementTime",
    y="MeasuredValue", 
    source = source
)
# Add range tool on the select graph, remove y grid
select.ygrid.grid_line_color = None
select.add_tools(range_tool)

def update_periodic_callback():
    global current_callback_id, last_temp

    measurement_interval = int(getTempFreq()[0])
    # Get interval and check if it's not zero
    if measurement_interval == 0:
        # Remove periodic callback if interval is 0
        if current_callback_id is not None:
            curdoc().remove_periodic_callback(current_callback_id)
            current_callback_id = None
            print("removed callback")
        return
    else:
        if measurement_interval != last_temp:
            last_temp = measurement_interval
            print("added callback")
            # Add a new periodic callback with the new interval
            current_callback_id = curdoc().add_periodic_callback(newTemp, measurement_interval * 1000)  # Convert seconds to milliseconds


def newTemp():

    # sleep necessary for flask to have time to update the values
    sleep(1)
    # Get new temp if last temp was 0 (to dodge errors)
    if last_temp != 0:
        url = "http://192.168.32.34:5000/api/get-temperature"
        x = requests.get(url)
        data = json.loads(x.text)

    # Get temperature readings
    url = "http://192.168.32.34:5000/api/set-temperature"
    x = requests.get(url)
    data = json.loads(x.text)
    print("received new data from app! ", data)
    # Get current index, bokeh bug when adding new data the index doesnt update
    current_index = source.data['index'][-1]
    # Change variables to pandas
    measurement = pd.DataFrame(data.items(), columns = ['MeasurementTime', 'MeasuredValue'])
    measurement['MeasurementTime'] = pd.to_datetime(measurement['MeasurementTime'])

    # Stream the new update
    source.stream(measurement)
    print("Source has been added!")
    source.data['index'][current_index + 1] = current_index + 1 
    ################################################
    # This part of code changes the graph's x_range to help user notice new data points
    last_time = measurement['MeasurementTime'].iloc[-1]

    # Set new x-range to focus on the last few hours around the new data
    p.x_range.start = last_time - pd.Timedelta(seconds=30)
    p.x_range.end = last_time + pd.Timedelta(seconds=30)
    if not isinstance(p.x_range, Range1d):
        p.x_range = Range1d(start=p.x_range.start, end=p.x_range.end)


# Implement button stylesheet to be similar to the ones in Flask
stylesheet = InlineStyleSheet(css="""
.bk-btn-default {
    color: #fff;
    background-color: #4285f4;
    border: none;
    cursor: pointer;
    padding: 10px;
    border-radius: 2px;
}
.bk-btn-default:hover {
    background-color: #1c4aa5;
  }
""")

# Implement button. Flask's buttons didn't work for new data addition
button = Button(label="Measure Temperature Now", button_type="default", stylesheets=[stylesheet], tags = ['Vienintelis-mygtukas'])
callback = CustomJS(code="measureTemperature();")
button.js_on_click(callback)

button.on_click(newTemp)


layout = column(p, select)

spacer1 = Spacer(height=30)

layout2 = column(layout, spacer1, button)

# Set root and and periodic callback of 5s which will check for database updates
curdoc().add_root(layout2)
curdoc().add_periodic_callback(update_periodic_callback, 5000)

