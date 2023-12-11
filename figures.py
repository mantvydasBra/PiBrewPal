from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter, HoverTool, WheelZoomTool, RangeTool, ColumnDataSource, Range1d
import pandas as pd

# Sample data (replace this with your actual dataset)
data = {
    'timestamp': [
        '2023-01-01 12:00:00', '2023-01-02 12:01:00', '2023-01-03 12:02:00', '2023-01-04 12:03:00', '2023-01-05 12:04:00',
        '2023-01-06 12:05:00', '2023-01-07 12:06:00', '2023-01-08 12:07:00', '2023-01-09 12:08:00', '2023-01-10 12:09:00',
        '2023-01-11 12:10:00', '2023-01-12 12:11:00', '2023-01-13 12:12:00', '2023-01-14 12:13:00', '2023-01-15 12:14:00',
        '2023-01-16 12:15:00', '2023-01-17 12:16:00', '2023-01-18 12:17:00', '2023-01-19 12:18:00', '2023-01-20 12:19:00',
        '2023-01-21 12:20:00', '2023-01-22 12:21:00', '2023-01-23 12:22:00', '2023-01-24 12:23:00', '2023-01-25 12:24:00',
        '2023-01-26 12:25:00', '2023-01-27 12:26:00', '2023-01-28 12:27:00', '2023-01-29 12:28:00', '2023-01-30 12:29:00',
        '2023-01-30 12:44:00', '2023-01-30 12:59:00', '2023-01-30 13:14:00', '2023-01-30 13:29:00', '2023-01-30 13:44:00', 
        '2023-01-30 13:59:00', '2023-01-30 14:14:00', '2023-01-30 14:29:00', '2023-01-30 14:44:00', '2023-01-30 14:59:00', 
        '2023-01-30 15:14:00', '2023-01-30 15:29:00', '2023-01-30 15:44:00', '2023-01-30 15:59:00', '2023-01-30 16:14:00'
    ],
    'temperature': [
        20.5, 21.0, 22.5, 22.5, 23.0, 23.0, 23.2, 22.8, 22.5, 22.8,
        22.9, 21.5, 21.8, 23.1, 25.0, 24.5, 24.0, 25.5, 26.0, 25.0,
        28.0, 29.0, 28.5, 27.5, 26.5, 27.0, 26.8, 26.0, 25.5, 25.0,
        20.5, 21.0, 22.5, 22.5, 23.0, 23.0, 23.2, 22.8, 22.5, 22.8,
        23.0, 23.2, 22.8, 22.5, 22.8
    ]

}

# Convert timestamp strings to datetime objects
data['timestamp'] = pd.to_datetime(data['timestamp'])

# Create a Bokeh ColumnDataSource
source = ColumnDataSource(data)

def drawLinePlot():    
    # Create a Bokeh figure
    p = figure(
        title='Temperature Change Over Time', 
        x_axis_label='Timestamp', 
        y_axis_label='Temperature (°C)', 
        sizing_mode = "stretch_width", 
        height = 350,
        width = 800,
        x_axis_type = 'datetime',
        x_range = (data['timestamp'][20], data['timestamp'][29])
    )

    # Plot the line graph
    line_renderer = p.line(
        x='timestamp', 
        y='temperature', 
        source=source, 
        line_width=2
    )

    # Add dots to each data point
    dots_renderer = p.circle(
        x='timestamp', 
        y='temperature', 
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
            ('Timestamp', '@timestamp{%Y-%m-%d %H:%M:%S}'),
            ('Temperature', '@temperature{0.0} °C'),
        ],
        formatters={'@timestamp': 'datetime'},
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
        x="timestamp",
        y="temperature", 
        source = source
    )

    # Add range tool on the select graph, remove y grid
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)

    # Return both objects to the main web server
    return p, select