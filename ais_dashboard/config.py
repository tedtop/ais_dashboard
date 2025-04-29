import os
import datashader as ds

base_path = '/home/alex/Desktop/AIS_Dashboard/coast_guard_ais'
output_root = os.path.abspath('./ais_renders')
x_range = (-18_000_000, 18_000_000)
y_range = (-4_000_000, 9_000_000)
canvas = ds.Canvas(plot_width=1920, plot_height=1080, x_range=x_range, y_range=y_range)
overlay_bounds = (x_range[0], y_range[0], x_range[1], y_range[1])
interval_options = ['1 Day', '3 Days', '5 Days', '7 Days', '14 Days', '1 Month']
