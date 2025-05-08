# Morton Analytics AIS Vessel Tracking Dashboard

A web-based geospatial visualization tool for exploring maritime vessel activity using AIS (Automatic Identification System) data. This dashboard visualizes aggregated ship locations as heat maps over time, allowing analysts to observe traffic patterns, congestion, and trends across the globe.

## Overview

The AIS Ship Traffic Dashboard processes time-stamped parquet files, converts them into visual heatmaps using Datashader, and presents these images on an interactive map with playback and time-based filtering capabilities.

### Features

- Visual heatmap representation of vessel density
- Time-based animation controls
- Customizable date range and interval selection
- Zoom and pan map navigation
- Efficient processing of large AIS datasets

## Project Components

The project consists of two main repositories:

1. **Data Processor** (`coast_guard_ais`)
   - Downloads AIS data from NOAA
   - Processes and converts to Parquet format
   - Organizes data in a hive-partitioned structure

2. **Dashboard** (`ais_dashboard`)
   - Interactive visualization interface
   - Data rendering engine
   - Animation and playback controls

## Technologies Used

- **Panel**: Interactive web UI framework
- **Holoviews**: Geospatial overlays with zoom/pan capabilities
- **Datashader**: Efficient rendering of massive datasets
- **PyArrow/Dask**: Efficient reading of columnar Parquet files
- **PIL/NumPy**: Image processing for visualization
- **Param**: Data-driven widget bindings
- **Colorcet**: Color mapping for heatmaps

## Installation

### Prerequisites

- Python 3.x
- Git

### Setup Instructions

1. Clone both repositories:
```bash
git clone https://github.com/tedtop/coast_guard_ais.git
git clone https://github.com/tedtop/ais_dashboard.git
```

2. Set up virtual environment:
```bash
python -m venv ais_project

# On Windows
ais_project\Scripts\activate

# On macOS or Linux
source ais_project/bin/activate
```

3. Install required packages for both repositories:
```bash
# For data processor
cd coast_guard_ais
pip install -r requirements.txt

# For dashboard
cd ../ais_dashboard
pip install -r requirements.txt
```

## Data Processing

1. Download and process AIS data:
```bash
cd coast_guard_ais
python zip2parquet.py
```

2. Move processed data to dashboard directory:
   - A folder named "year=20xx" will be created
   - Create an empty folder named "coast_guard_ais"
   - Move the "year=20xx" folder into "coast_guard_ais"
   - Move the "coast_guard_ais" folder to the "ais_dashboard" directory

## Running the Dashboard

```bash
cd ais_dashboard
source ais_project/bin/activate  # Activate your virtual environment
panel serve --autoreload --show main.py --static-dirs assets=assets
```

**Note**: An internet connection is required to run this software properly, as it pulls a map from OpenStreetMap.com.

## Using the Dashboard

### Control Panel

1. Select Date Range (e.g., Jan 1, 2024 to Jan 11, 2024)
2. Select Interval (e.g., "1 Day" or "3 Days")
3. Click "Generate Visualization"
4. Wait for the rendering process to complete (monitor progress in the log pane)

### Viewer

- Click ▶️ to play the animation
- Use ◀️ and ▶️ to step through frames
- View timestamp of the currently loaded frame
- Zoom and pan to explore areas of interest

## Directory Structure

Expected AIS .parquet files should follow this structure:
```
coast_guard_ais/year=YYYY/month=MM/day=DD/hour=HH/AIS_YYYY_MM_DD_processed_hourHH.parquet
```

Each file should contain at least LAT and LON columns.

## Maintenance

### To maintain usability:
- Ensure new parquet files are written to the correct directory structure
- Run "Generate Visualization" for new date ranges as data is added

### To reset:
- Delete PNGs in output_root/interval/*
- Re-run the renderer for the desired range

## Manual Rendering (if needed)

```python
from renderer import AISRenderer
from config import base_path, output_root, canvas

renderer = AISRenderer(base_path, output_root, canvas)
renderer.render("2024-01-01", "2024-01-10", "1 Day")
```

## Architecture

The dashboard is organized into the following core modules:

- **Data Renderer** (`renderer.py`): Converts raw hourly AIS parquet data into 2D PNG visualizations
- **Control Panel** (`control.py`): Provides date and interval selectors for controlling visualization range
- **Viewer Panel** (`viewer.py`): Loads and displays PNG visualizations as map overlays with animation controls
- **Dashboard Wrapper** (`dashboard.py`): Combines viewer and controls into a cohesive interface
- **Entry Script** (`main.py`): Launches the dashboard server
- **Configuration** (`config.py`): Centralized setup of file paths, map ranges, and available intervals

## Contributing

Please feel free to submit issues or pull requests for any bugs or enhancements.

## License

[MIT License](LICENSE)

## Acknowledgements

- Data provided by NOAA AIS data repository
- Developed by Sixth Sense Solutions for Morton Analytics
