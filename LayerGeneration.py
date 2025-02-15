from PIL import Image, ImageTk
import requests
from io import BytesIO
import pandas as pd
import numpy as np
from src.HeatMaps import *
from src.ContourMaps import *
from src.DepthChangeMaps import *
from src.DepthChange2 import *
import time
import os
from src.analyses import *

class GPSBounds():
    def __init__(self, extent=None, lonmin=0, latmax=0, latmin=0, lonmax=0):
        if isinstance(extent, dict):
            self.latmin = extent['latmin']
            self.latmax = extent['latmax']
            self.lonmin = extent['lonmin']
            self.lonmax = extent['lonmax']
        elif isinstance(extent, list):
            self.lonmin = extent[0]
            self.lonmax = extent[1]
            self.latmin = extent[2]
            self.latmax = extent[3]
        elif isinstance(extent, GPSBounds):
            self.lonmin = extent.lonmin
            self.lonmax = extent.lonmax
            self.latmin = extent.latmin
            self.latmax = extent.latmax
        else:
            self.latmin = latmin
            self.latmax = latmax
            self.lonmin = lonmin
            self.lonmax = lonmax
    def noaabox(self):
        return str(self.lonmin)+','+str(self.latmin)+','+str(self.lonmax)+','+str(self.latmax)
    def array(self): #lon_min, lat_max, lon_max, lat_min
        return [self.lonmin, self.lonmax, self.latmin, self.latmax]
    def __str__(self):
        return f"GPSBounds(Longitude: {self.lonmin} - {self.lonmax}, Latitude {self.latmin} - {self.latmax})"


class LayerGenerator():
    def __init__(self):
        super().__init__()
        self.analysis_method = "Heatmap"
        self.roll = 1
        self.width = 0.5
        self.resolution = 1024

        self.tk_image = None
        self.image_on_canvas = None

        # Variables to keep track of dragging
        self.start_x = 0
        self.start_y = 0
        self.offset_x = 0
        self.offset_y = 0

        self.net_x = 0
        self.net_y = 0

        #lon_min, lat_max, lon_max, lat_min
        self.GPS = GPSBounds()

    def calculate_size(self, max_width):
        xmin, xmax, ymin, ymax = self.GPS.array()
        aspect_ratio = (xmax - xmin) / (ymax - ymin)  # Calculate aspect ratio
        width = max_width
        height = int(width / aspect_ratio)  # Adjust height based on aspect ratio
        return f"{width},{height}"  # Return size as "width,height"
    
    def set_sizing(self):
        self.size_parameter = self.calculate_size(self.resolution)

    def set_resolution(self, res=None):
        if res == None:
            res = self.resolution
        self.resolution = res
        self.set_sizing()
        
    def set_analysis(self, selection):
        self.analysis_method = selection
        
    def set_roll(self, roll):
        self.roll = roll
        
    def set_width(self, width): 
        self.width = width

    def set_gps_bounds(self, extent):
        self.set_GPS(GPSBounds(extent))

    def set_GPS(self, gps):
        self.GPS = gps
    
    def load_data(self, cache_file, debug_prints=False, event = None):
        self.image = self.make_image(cache_file, debug_prints)
        return self.image
    
    def make_image(self, cache_file, debug_prints=False):
        start_time = time.time()
        mid_time1, mid_time2, mid_time3, mid_time4 = 0,0,0,0
        if debug_prints:
            print("Start time", f"{start_time - start_time}", f"{start_time - start_time}")

        if os.path.exists(cache_file):
        # if False:
            image = Image.open(cache_file)
        else:
            url = 'https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_tiles_mosaic/ImageServer/exportImage'
            params = {
                'bbox': self.GPS.noaabox(),
                'size': self.size_parameter, 
                'bboxSR': '4326',  
                'imageSR': '4326',
                'format': 'tiff',  
                'f': 'image'  
            }
            try:
                response = requests.get(url, params=params)
            except:
                return None
            mid_time1 = time.time()
            if debug_prints:
                print("Retrieve data", f"{mid_time1 - start_time}", f"{mid_time1 - start_time}")
            # print(url, params)
            image = None
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if not ("image" in content_type):
                    print(f"Unexpected content type: {content_type}")
                    print(f"Response content: {response.text}")  # Log non-image content
                else:
                    try:
                        image = Image.open(BytesIO(response.content))
                        image.load()  # Force Pillow to fully load the image
                    except Exception as e:
                        image = None
                        print(f"Error loading image: {e}")
            else:
                print(f"Failed to load data. Status code: {response.status_code}")
            mid_time2 = time.time()
            if debug_prints:    
                print("Load image", f"{mid_time2 - mid_time1}", f"{mid_time2 - start_time}")
            if image != None:
                image.save(cache_file)
        if image != None:
            image_array = np.array(image)
            df = pd.DataFrame(image_array)

            roll = self.roll
            curr_method = self.analysis_method
            width = self.width

            
            if curr_method.lower() == 'heatmap':
                img = seaborn_heat_map(df)
            elif curr_method.lower() == 'inshore-navigation':
                img = inshore_navigation(df)
            elif curr_method.lower() == "contour-map":
                img = contour_map_type1_optimized(df, roll, width)
            elif curr_method.lower() == "depth-change-map":
                img = depth_change(df)
            elif curr_method.lower() == "depth-change-frequency-map":
                img = depth_change_frequency(df)
            elif curr_method.lower() == "old-heatmap":
                img = heat_map_type1(df, width)
            elif curr_method.lower() == "old-contour-map":
                img = contour_map_type1(df, roll, width)
            mid_time3 = time.time()
            if debug_prints:
                print("Process image", f"{mid_time3 - mid_time2}", f"{mid_time3 - start_time}")
            # img = img.resize((self.resolution, self.resolution), Image.NEAREST)
            img.save("img/output_image.png", format="PNG")
            mid_time4 = time.time()
            if debug_prints:
                print("Save image", f"{mid_time4 - mid_time3}", f"{mid_time4 - start_time}")
            return img
        else:
            print(f"Failed to load data. Status code: {response.status_code}")
            return None
