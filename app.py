from flask import Flask, render_template, send_file
from flask_session import Session
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
import json
import time
import math
import threading
# import src.FishFinderTools as FishFinderTools
from src.LayerGeneration import LayerGenerator
import shutil

app = Flask(__name__)

# Configure the session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"  # You can use other backends like Redis
Session(app)

layer_gen = LayerGenerator()
layer_gen.resolution = 128

with app.app_context():
    if os.path.exists('img/tile'):
        shutil.rmtree('img/tile/')
    os.makedirs('img/tile', exist_ok=True)
    Session.tile_events = {}
    Session.reload = threading.Event()
    Session.reload.set()
    Session.tile_events_lock = threading.Lock()
# n = 3
# for res in range(1000,1001):
#     start = time.time()
#     for i in range(n):
#         layer_gen.set_analysis("depth-change")
#         layer_gen.set_gps_bounds({"lonmin": -82.0, "lonmax": -79.0, "latmin": 24.0, "latmax": 26.0})
#         layer_gen.set_resolution(res)
#         layer_gen.load_data(True)
#     print(f"Resolution {res} time {(time.time() - start)/n} s")
#     print(f"Resolution {res} efficiency {(time.time() - start)/3/(res**2)} s")
# os._exit(0)

@app.route('/reload-layer/<string:coord_bounds>_<string:res>_<string:analysis>_<string:smoothness>_<string:width>')
def reload_layer(coord_bounds, res, analysis, smoothness, width):
    Session.reload.clear()
    try:
        if os.path.exists('img/tile'):
            shutil.rmtree('img/tile/')
        os.makedirs('img/tile', exist_ok=True)
    except:
        pass

    print("Reloading layer with", coord_bounds, res, analysis, smoothness, width)
    layer_gen.set_resolution(int(res))
    layer_gen.set_analysis(analysis)
    layer_gen.set_roll(int(smoothness))
    layer_gen.set_width(float(width))
    extent = json.loads(coord_bounds)
    layer_gen.set_gps_bounds(extent)
    Session.reload.set()
    
    return "OK"

def tile_to_lat_lon(tile_x, tile_y, zoom):
    n = 2.0 ** zoom
    lon_min = tile_x / n * 360.0 - 180.0
    lon_max = (tile_x + 1) / n * 360.0 - 180.0
    lat_rad_max = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat_rad_min = math.atan(math.sinh(math.pi * (1 - 2 * (tile_y + 1) / n)))
    lat_min = math.degrees(lat_rad_min)
    lat_max = math.degrees(lat_rad_max)
    return lon_min, lon_max, lat_min, lat_max

def lat_lon_to_tile(lat, lon, zoom):
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(math.radians(lat)) + 1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return x, y

def test_info_image(text, output_name):
    # Create a square image
    width, height = int(1.69*256)-1,255  # Define the size of the square image
    img = Image.new('RGB', (width, height), color='red')

    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((0, 0), text, (255, 255, 255), font=font)

    square_size = width // 4
    square_x0 = (width - square_size) // 2
    square_y0 = (height - square_size) // 2
    square_x1 = square_x0 + square_size
    square_y1 = square_y0 + square_size
    draw.rectangle([square_x0, square_y0, square_x1, square_y1], outline="blue", fill="blue")

    border_size = 1
    img_with_border = ImageOps.expand(img, border=border_size, fill='black')
    img_with_border.save(output_name, format="PNG")
    return output_name

def crop_image(img_name, x_min=0, x_max=1, y_min=0, y_max=1, output_name="img/temp.png"):
    img = Image.open(img_name)
    width, height = img.size

    x_min_px = int(round(x_min * width))
    x_max_px = int(round(x_max * width))
    y_min_px = int(round(y_min * height))
    y_max_px = int(round(y_max * height))

    img = img.crop((x_min_px, y_min_px, x_max_px, y_max_px))
    # border_size = 1
    # img = ImageOps.expand(img, border=border_size, fill='black')
    # img.save(output_name, format="PNG")
    # img = anti_alias(img)
    img.save(output_name, format="PNG")
    return output_name

def anti_alias(img):
    return img.resize((4*img.width, 4*img.height), Image.Resampling.LANCZOS)

@app.route('/tile/<int:level>_<int:row>_<int:col>')
def serve_tile(level, row, col):
    start_time = time.time()
    Session.reload.wait()
    filename = f"img/tile/{level}_{row}_{col}.png"
    if os.path.exists(filename):
        print("Serving cached tile", level, row, col, "Time taken:", time.time() - start_time)
        return send_file(filename, mimetype="image/png")
    
    #batch number
    n = 0

    # Load the encapsulating tile from the previous level (level - n)
    parent_level = level - n
    parent_row = row // (2**n)
    parent_col = col // (2**n)

    # Create an event for the parent tile if it doesn't exist
    # with Session.tile_events_lock:
    #     if (parent_level, parent_row, parent_col) not in Session.tile_events:
    #         Session.tile_events[(parent_level, parent_row, parent_col)] = threading.Event()
    #         print("Same time?")
    #     else:
    #         print("Waiting for tile to load ", parent_level, parent_row, parent_col)
    #         # Wait for the parent tile to be loaded
    #         Session.tile_events[(parent_level, parent_row, parent_col)].wait()

    parent_filename, x_min, x_max, y_min, y_max, output_name = generate_tile(level, row, col, parent_level, parent_row, parent_col)

    # Signal that the tile is done loading
    # if (parent_level, parent_row, parent_col) in Session.tile_events:
    #     Session.tile_events[(parent_level, parent_row, parent_col)].set()
    #     del Session.tile_events[(parent_level, parent_row, parent_col)]
    
    if parent_filename == "":
        return send_file("img/blank.png", mimetype="image/png")
    
    # Crop the parent tile to create the current tile
    crop_image(parent_filename, x_min, x_max, y_min, y_max, output_name)
    # test_info_image(f"{level}_{row}_{col}/{parent_level}_{parent_row}_{parent_col}", output_name)
    
    print("Serving generated tile", level, row, col, "Time taken:", time.time() - start_time)
    return send_file(output_name, mimetype="image/png")

def generate_tile(level, row, col, parent_level, parent_row, parent_col):
    if parent_level < 0:
        print("Serving blank image - level too low.")
        return "", 0, 0, 0, 0, ""

    # Calculate the cropping coordinates based on longitude and latitude
    lon_min, lon_max, lat_min, lat_max = tile_to_lat_lon(col, row, level)
    parent_lon_min, parent_lon_max, parent_lat_min, parent_lat_max = tile_to_lat_lon(parent_col, parent_row, parent_level)

    x_min = (lon_min - parent_lon_min) / (parent_lon_max - parent_lon_min)
    x_max = (lon_max - parent_lon_min) / (parent_lon_max - parent_lon_min)
    y_min = 1-(lat_max - parent_lat_min) / (parent_lat_max - parent_lat_min)
    y_max = 1-(lat_min - parent_lat_min) / (parent_lat_max - parent_lat_min)

    parent_filename = f"img/tile/{parent_level}_{parent_row}_{parent_col}.png"
    output_name = f"img/tile/{level}_{row}_{col}_temp.png"

    if not os.path.exists(parent_filename):
        # Load the parent tile if it doesn't exist
        lon_min, lon_max, lat_min, lat_max = parent_lon_min, parent_lon_max, parent_lat_min, parent_lat_max#tile_to_lat_lon(parent_col, parent_row, parent_level)
        extent = {"lonmin": lon_min, "lonmax": lon_max, "latmin": lat_min, "latmax": lat_max}
        layer_gen.set_gps_bounds(extent) 
        layer_gen.set_resolution()
        if not os.path.exists(f"img/noaa/{layer_gen.analysis_method}"):
            os.mkdir(f"img/noaa/{layer_gen.analysis_method}")
        image = layer_gen.load_data(cache_file=f"img/noaa/{layer_gen.analysis_method}/{parent_level}_{parent_row}_{parent_col}.tiff")
        if image == None:
            print("Serving blank image - NOAA error")
            return "", 0, 0, 0, 0, ""
        image.save(parent_filename, format="PNG")
    return parent_filename, x_min, x_max, y_min, y_max, output_name

@app.route('/map')
def map_page():
    return render_template('map.html', map_layers=[{"id":0}])

@app.route("/about-us")
def about_us():
    return render_template("about_us.html", section="about")

@app.route("/services")
def services():
    return render_template("about_us.html", section="services")

@app.route("/team")
def team():
    return render_template("about_us.html", section="team")

@app.route("/contact-us")
def contact():
    return render_template("about_us.html", section="contact")

@app.route('/')
def index():
    return map_page()


if __name__ == '__main__':
    app.run(debug=True, port=8080, threaded=True)

