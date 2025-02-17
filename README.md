# FishFinder
 
FishFinder is an interactive bathymetry visualization tool designed for exploring underwater topography through a web-based interface. It allows users to analyze and interact with bathymetric data easily, making it ideal for marine researchers, fishermen, and oceanographers who need precise and detailed underwater terrain visualizations.  

The project began as a personal project to try to find fishing spots in the Florida Keys (an area I often fish), but has since developed into a nearly completed website website which I plan to release in the near future.  

## How It Works
FishFinder processes and visualizes bathymetric data using a local server. The backend, written in Python, handles data loading, processing, and serving, while the frontend, built with HTML, JavaScript, and CSS, provides a highly interactive experience.  
- The user navigates through underwater maps by dragging and zooming.
- The application loads bathymetric data dynamically to ensure smooth performance.
- Users can switch between different visualization modes, such as contour mapping and heatmap rendering.
- GPS coordinates are continuously updated to provide real-time location tracking.
- I am currently working on designing a program to algorithmically identify the best fishing spots based on parameterization of the bathymetric data. 

## System Architecture & Data Sourcing
FishFinder operates as a locally hosted web application. The backend, implemented in Python, processes bathymetric data and serves it through a Flask-based web server. The frontend, built with HTML, JavaScript, and CSS, provides an interactive interface for users to navigate and analyze the data. The system is designed for efficient performance, dynamically loading and updating bathymetric data as users interact with the interface.  

The data for FishFinder is sourced from NOAA's freely available bathymetric dataset. The data is called through the associated API, which takes a boundary box and a level of resolution and returns the data in a tiff image format. This tiff is then read into a pandas dataframe, which is used in the visualization algorithms and is eventually converted to images to be displayed. 
