from db import loadTemperature
from bokeh.layouts import column
from bokeh.plotting import figure, curdoc
from bokeh.models import DatetimeTickFormatter, HoverTool, WheelZoomTool, RangeTool, ColumnDataSource

# Load temperature from database
df = loadTemperature()

# Create a Bokeh ColumnDataSource
source = ColumnDataSource(df)


# Create a Bokeh figure
p = figure(
    title='Temperature Change Over Time', 
    x_axis_label='Timestamp', 
    y_axis_label='Temperature (°C)', 
    sizing_mode = "stretch_width", 
    height = 350,
    width = 800,
    x_axis_type = 'datetime',
    x_range = (df['MeasurementTime'][0], df['MeasurementTime'][9])
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

# # Define a callback to update the plot data
# def update():
#     new_data = dict(x=[random.random()], y=[random.random()])
#     source.stream(new_data)

# # Add a periodic callback to update the plot every second
# curdoc().add_periodic_callback(update, 1000)


layout = column(p, select)
# code = "<h1>loading finished</h1>"
# callback = CustomJS(args = dict(), code = code) 
# Add the plot to the current document
# curdoc().add_root(spinner)
curdoc().add_root(layout)

# curdoc().js_on_event("document_ready")