import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import pandas as pd
import numpy as np
from HeatMaps import *
from ContourMaps import *
from DepthChangeMaps import *
from DepthChange2 import *

class BathymetryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fish Finder")
        self.screen_dimension = 900
        self.scn_width = self.screen_dimension
        self.scn_height = self.screen_dimension
        self.geometry(str(self.scn_width) + 'x' + str(self.scn_height))
        self.resizable(False, False)

        self.img_width, self.img_height = (self.screen_dimension, self.screen_dimension)
        self.canvas = tk.Canvas(self, width=self.img_width, height=self.img_height)

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.analysis_method = tk.StringVar(value="Heatmap")
        self.analysis_dropdown = tk.OptionMenu(self.top_frame, self.analysis_method, "Heatmap", "Boating Map", "Contour Map", "Depth Change Map", "Depth Change Frequency Map", command=self.update_analysis)
        self.analysis_dropdown.pack(side=tk.RIGHT, padx=5)
        analysis_label = tk.Label(self.top_frame, text="Analysis:")
        analysis_label.pack(side=tk.RIGHT, padx=5)

        # Label and Dropdown for Roll
        self.roll = tk.IntVar(value=1)
        self.roll_dropdown = tk.OptionMenu(self.top_frame, self.roll, 0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 50)
        self.roll_dropdown.pack(side=tk.RIGHT, padx=5)
        roll_label = tk.Label(self.top_frame, text="Roll Pixels:")
        roll_label.pack(side=tk.RIGHT, padx=5)

        # Label and Dropdown for Width
        self.width = tk.DoubleVar(value=0.5)
        self.width_dropdown = tk.OptionMenu(self.top_frame, self.width, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 
                                            7.5, 10, 12.5, 15, 20, 30, 40, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 1000)
        self.width_dropdown.pack(side=tk.RIGHT, padx=5)
        width_label = tk.Label(self.top_frame, text="Layer Width:")
        width_label.pack(side=tk.RIGHT, padx=5)

        resolution_label = tk.Label(self.top_frame, text="Resolution:")
        resolution_label.pack(side=tk.LEFT, padx=5)

        # Scale for Resolution
        self.resolution_scale = tk.Scale(
            self.top_frame,
            from_=1, to=10,
            orient=tk.HORIZONTAL,
            length=200,
            tickinterval=1,
            label="Low             Medium             High",
            command=self.update_resolution
        )
        self.resolution_scale.set(3) 
        self.resolution_scale.pack(side=tk.LEFT, padx=5)

        self.resolution_correspondence = {
            1:100, 2:150, 3: 225, 4: 450, 5: 900, 6: 1500, 7: 300, 8: 500, 9:10000, 10: 20000
        }

        self.canvas.pack(expand=True)

        self.tk_image = None
        self.image_on_canvas = None

        #self.tk_image = ImageTk.PhotoImage(self.image)
        #self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Variables to keep track of dragging
        self.start_x = 0
        self.start_y = 0
        self.offset_x = 0
        self.offset_y = 0

        self.net_x = 0
        self.net_y = 0

        # Bind mouse events for dragging
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<MouseWheel>", self.zoom) 
        self.bind("<r>", self.load_data)
        self.bind("<i>", self.zoom_in)
        self.bind("<o>", self.zoom_out)
        self.bind("<t>", self.test_print)
        self.bind_all('<x>', self.close_application)

        self.current_GPS = [-81.053890, 24.745288, -81.008397, 24.718449]
        self.image_GPS = [-81.053890, 24.745288, -81.008397, 24.718449] #this one only changes when image is reloaded
        self.set_sizing()
        self.current_GPS_width_step = (self.current_GPS[2] - self.current_GPS[0]) / 800
        self.current_GPS_height_step = (self.current_GPS[3] - self.current_GPS[2]) / 800
        #self.box = str(str(self.current_GPS[0])+','+str(self.current_GPS[1])+','+str(self.current_GPS[2])+','+str(self.current_GPS[3]))

        self.load_data()

    def test_print(self, event):
        print(self.current_GPS)

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_in(event)
        elif event.delta < 0: 
            self.zoom_out(event)

    def zoom_in(self, event):
        print('zoom in')
        canvas_relative_x = event.x
        canvas_relative_y = event.y - 100 #-100 because of the top buttons and scroll are changing location

        x = (canvas_relative_x / self.screen_dimension)*(self.current_GPS[2] - self.current_GPS[0]) + self.current_GPS[0]
        y = (canvas_relative_y / self.screen_dimension)*(self.current_GPS[3] - self.current_GPS[1]) + self.current_GPS[1]

        new_top_left_x = x- (0.5*(self.current_GPS[2] - self.current_GPS[0]))*((x - self.current_GPS[0]) / (self.current_GPS[2] - self.current_GPS[0]))
        new_top_left_y = y- (0.5*(self.current_GPS[3] - self.current_GPS[1]))*((y - self.current_GPS[1]) / (self.current_GPS[3] - self.current_GPS[1]))
        new_bottom_right_x = x+ (0.5*(self.current_GPS[2] - self.current_GPS[0]))*((self.current_GPS[2] - x) / (self.current_GPS[2] - self.current_GPS[0]))
        new_bottom_right_y = y+ (0.5*(self.current_GPS[3] - self.current_GPS[1]))*((self.current_GPS[3] - y) / (self.current_GPS[3] - self.current_GPS[1]))

        self.current_GPS[0] = new_top_left_x
        self.current_GPS[1] = new_top_left_y
        self.current_GPS[2] = new_bottom_right_x
        self.current_GPS[3] = new_bottom_right_y

        self.load_data()
    
    def zoom_out(self, event):
        print('zoom out')
        canvas_relative_x = event.x
        canvas_relative_y = event.y - 100 #-100 because of the top buttons and scroll are changing location

        x = (canvas_relative_x / self.screen_dimension)*(self.current_GPS[2] - self.current_GPS[0]) + self.current_GPS[0]
        y = (canvas_relative_y / self.screen_dimension)*(self.current_GPS[3] - self.current_GPS[1]) + self.current_GPS[1]

        new_top_left_x = x- (2*(self.current_GPS[2] - self.current_GPS[0]))*((x - self.current_GPS[0]) / (self.current_GPS[2] - self.current_GPS[0]))
        new_top_left_y = y- (2*(self.current_GPS[3] - self.current_GPS[1]))*((y - self.current_GPS[1]) / (self.current_GPS[3] - self.current_GPS[1]))
        new_bottom_right_x = x+ (2*(self.current_GPS[2] - self.current_GPS[0]))*((self.current_GPS[2] - x) / (self.current_GPS[2] - self.current_GPS[0]))
        new_bottom_right_y = y+ (2*(self.current_GPS[3] - self.current_GPS[1]))*((self.current_GPS[3] - y) / (self.current_GPS[3] - self.current_GPS[1]))

        self.current_GPS[0] = new_top_left_x
        self.current_GPS[1] = new_top_left_y
        self.current_GPS[2] = new_bottom_right_x
        self.current_GPS[3] = new_bottom_right_y

        self.load_data()

    def close_application(self, event):
        self.quit()
        self.destroy()

    def make_buttons(self):
        self.analysis_method = tk.StringVar(self)
        self.analysis_method.set("Heatmap")  # Default value
        
        self.analysis_menu = tk.OptionMenu(self, self.analysis_method, "Heatmap", "Boating Map", "Contour Map", "Depth Change Map", "Depth Change Frequency Map", command=self.update_analysis)
        self.analysis_menu.pack()
        self.canvas.pack()

    def set_sizing(self):
        res = self.resolution_correspondence[self.resolution_scale.get()]
        self.size_parameter = str(res) + ', ' + str(res)
    def update_resolution(self, res):
        self.resolution_scale.set(res)
        print(f"Selected resolution: {res}")
        self.load_data()
    def update_analysis(self, selection):
        """Update the analysis method based on the dropdown selection."""
        # Change the analysis method and refresh the image
        self.analysis_method.set(selection)
        print(f"Selected analysis method: {selection}")
        self.load_data()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
    
    def on_mouse_drag(self, event):
        self.offset_x = event.x - self.start_x
        self.offset_y = event.y - self.start_y

        self.net_x += self.offset_x
        self.net_y += self.offset_y

        self.canvas.move(self.image_on_canvas, self.offset_x, self.offset_y)
        
        self.start_x = event.x
        self.start_y = event.y

        x_mult = abs(self.offset_x)
        y_mult = abs(self.offset_y)

        self.current_GPS[0] = (self.current_GPS[0] + x_mult*self.current_GPS_width_step) if self.offset_x < 0 else self.current_GPS[0] - x_mult*self.current_GPS_width_step
        self.current_GPS[1] = (self.current_GPS[1] + y_mult*self.current_GPS_height_step) if self.offset_y < 0 else self.current_GPS[1] - y_mult*self.current_GPS_height_step
        self.current_GPS[2] = (self.current_GPS[2] + x_mult*self.current_GPS_width_step) if self.offset_x < 0 else self.current_GPS[2] - x_mult*self.current_GPS_width_step
        self.current_GPS[3] = (self.current_GPS[3] + y_mult*self.current_GPS_height_step) if self.offset_y < 0 else self.current_GPS[3] - y_mult*self.current_GPS_height_step


    def on_button_release(self, event):
        self.offset_x = 0
        self.offset_y = 0

    def load_data(self, event=None):
            
        img = self.make_image()

        self.image = img
        self.tk_image = ImageTk.PhotoImage(self.image)

        '''
        if self.image_on_canvas:
            self.canvas.itemconfig(self.image_on_canvas, image=self.tk_image)
        else:
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        #self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        '''            

        #self.canvas.delete("all")  # Clear all items from the canvas
        self.canvas.delete(self.image_on_canvas)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.img_width, self.img_height = img.size

        self.title(f"Fish Finder - Size: {self.img_width}x{self.img_height}")

        width = self.image.width
        height = self.image.height

        self.current_GPS_width_step = (self.current_GPS[2] - self.current_GPS[0]) / width
        self.current_GPS_height_step = (self.current_GPS[3] - self.current_GPS[1]) / height

        self.net_x = 0
        self.net_y = 0

        print(self.current_GPS)

    
    def make_image(self):
        self.box = str(str(self.current_GPS[0])+','+str(self.current_GPS[1])+','+str(self.current_GPS[2])+','+str(self.current_GPS[3]))
        #self.box = str(str(round(self.current_GPS[0], 5))+','+str(round(self.current_GPS[1], 5))+','+str(round(self.current_GPS[2], 5))+','+str(round(self.current_GPS[3], 5)))
                
        self.set_sizing()

        url = 'https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_tiles_mosaic/ImageServer/exportImage'
        params = {
            'bbox': self.box,  
            'bboxSR': '4326',  
            'size': self.size_parameter,  
            'imageSR': '4326',  
            'format': 'tiff',  
            'f': 'image'  
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            self.image_GPS = self.current_GPS

            self.last_loaded_GPS = self.current_GPS

            image_array = np.array(image)
            df = pd.DataFrame(image_array)

            roll = self.roll.get()
            curr_method = self.analysis_method.get()
            width = self.width.get()
            
            if curr_method == 'Heatmap':
                img = heat_map_type1(df, width)
            elif curr_method == "Boating Map":
                img = contour_map_type1(df, roll, width)
            elif curr_method == "Contour Map":
                img = depth_change_downward(df)
            elif curr_method == "Depth Change Map":
                img = depth_change_frequency(df)
            elif curr_method == "Depth Change Frequency Map":
                img = depth_change_frequency(df)

            if self.resolution_scale.get()<5:
                return img.resize((self.screen_dimension, self.screen_dimension), Image.NEAREST)
            else:
                return img
        else:
            print(f"Failed to load data. Status code: {response.status_code}")


if __name__ == "__main__":

    app = BathymetryApp()
    app.mainloop()
