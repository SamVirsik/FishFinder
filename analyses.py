import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
#import io

def seaborn_heat_map(df):
    """
    Heatmap created using seaborn heatmapping. 
    To change the scale you simply need to change the 'min_value' parameter. 
    The more negative it is the greater the range. 

    Other colors scales of heat maps are also possible, changing the viridis parameter. 
    """
    min_value, max_value = -5, 1

    clipped_data = df.clip(lower=min_value, upper=max_value)
    normalized_data = (clipped_data - min_value) / (max_value - min_value)

    normalized_data = normalized_data.fillna(0).replace([np.inf, -np.inf], 0)

    colormap = plt.get_cmap("viridis")
    colored_data = colormap(normalized_data.values)[:, :, :3]  # Remove alpha channel

    image = Image.fromarray((colored_data * 255).astype(np.uint8))

    return image

def depth_change_frequency(df):
    '''
    Makes a grayscale image for which the intensity of gray is based on 
    the number of surrounding pixels for which there was a downward 
    depth decrease. 
    '''
    from PIL import Image
    import numpy as np

    num_rows, num_cols = df.shape

    # Precompute downward changes
    blank = np.zeros_like(df.values, dtype=np.uint8)
    blank[1:] = (df.values[1:] < df.values[:-1]).astype(np.uint8)

    # Compute 3x3 neighborhood sums using convolution
    from scipy.ndimage import convolve
    kernel = np.ones((3, 3), dtype=np.uint8)
    neighborhood_sums = convolve(blank, kernel, mode='constant', cval=0)

    # Prepare color mapping
    land_color = (246, 185, 33) 

    # Create a blank image
    image_array = np.zeros((num_rows, num_cols, 3), dtype=np.uint8)

    # Assign colors based on conditions
    land_mask = (df.values >= 0)
    grayscale_values = (255 * (neighborhood_sums / 8)).astype(np.uint8)

    # Apply colors
    image_array[land_mask] = land_color
    image_array[~land_mask] = np.stack([grayscale_values, grayscale_values, grayscale_values], axis=-1)[~land_mask]

    # Convert the array to an image
    image = Image.fromarray(image_array, 'RGB')
    return image




def depth_change(df):
    '''
    Plots black as downward depth increase, and white as the same or decrease. 
    For texture. 
    '''
    from PIL import Image
    import numpy as np

    num_rows, num_cols = df.shape

    # Precompute values for efficiency
    blank = np.zeros_like(df.values, dtype=np.uint8)
    blank[1:] = (df.values[1:] < df.values[:-1]).astype(np.uint8)

    # Prepare color mapping
    land_color = (246, 185, 33)  
    depth_decrease_color = (255, 255, 255)  # White
    depth_increase_color = (0, 0, 0)  # Black

    # Create a blank image
    image_array = np.zeros((num_rows, num_cols, 3), dtype=np.uint8)

    # Assign colors based on conditions
    land_mask = (df.values >= 0)
    depth_decrease_mask = (blank == 1) & ~land_mask

    image_array[land_mask] = land_color
    image_array[depth_decrease_mask] = depth_decrease_color
    image_array[~land_mask & ~depth_decrease_mask] = depth_increase_color

    # Convert the array to an image
    image = Image.fromarray(image_array, 'RGB')
    return image


def boating_map(df, width): 
    number_rows, number_columns = df.shape
    image = Image.new('RGB', (number_columns, number_rows), color = 'white')
    pixels = image.load()
    
    colorList = [(139, 69, 19), (212, 255, 1), (190, 255, 1), (166, 255, 17), (139, 255, 17), 
                 (115, 255, 49), (83, 255, 84), (53, 255, 114), (53, 255, 147), (53, 255, 199), 
                 (17, 255, 220), (0, 255, 249), (0, 245, 249), (0, 226, 249), (0, 212, 242), 
                 (0, 198, 242), (0, 182, 242), (0, 167, 242), (0, 150, 242), (0, 128, 242), 
                 (0, 110, 218), (0, 88, 218), (0, 61, 215), (0, 30, 215), (0, 0, 207), (0, 0, 187), 
                 (0, 0, 163), (0, 0, 140), (0, 0, 128), (0, 0, 108), (0, 0, 88)]

    for row_index, row_data in df.iterrows():
        for col_name in df.columns:
            mValue = row_data[col_name]
            fValue = mValue*3.28084 #foot value

            scaled = ((abs(fValue)) - fValue) / 2

            if scaled == 0.0:
                pixels[col_name, row_index] = colorList[0]
            else:
                scaled = int(scaled/width) + 1
            
            if (scaled > len(colorList)-2):
                pixels[col_name, row_index] = colorList[len(colorList)-1]
            else:
                pixels[col_name, row_index] = colorList[int(scaled)]


    
    return image

def inshore_navigation(df):
    # Define the RGB color mapping for depth ranges
    color_mapping = np.array([
        ((0, float('inf')), (246, 185, 33)),      # 0+ depth
        ((-1, 0), (124, 153, 100)),              # 0 to -1
        ((-2, -1), (180, 175, 132)),             # -1 to -2
        ((-6, -2), (224, 206, 192)),             # -2 to -6
        ((-20, -6), (192, 198, 196)),            # -6 to -20
        ((-30, -20), (202, 207, 208)),           # -20 to -30
        ((-50, -30), (138, 177, 189)),           # -30 to -50
        ((float('-inf'), -50), (255, 255, 255))  # Below -50
    ], dtype=object)
    
    # Convert DataFrame to a NumPy array in feet
    df_array = df.to_numpy() * 3.28084  # Convert meters to feet
    
    # Create an empty array for storing RGB values
    number_rows, number_columns = df_array.shape
    rgb_array = np.zeros((number_rows, number_columns, 3), dtype=np.uint8)
    
    # Apply color mapping based on depth ranges
    for depth_range, color in color_mapping:
        mask = (df_array >= depth_range[0]) & (df_array < depth_range[1])
        rgb_array[mask] = color  # Assign the RGB color for the matching depth range
    
    # Create an image from the RGB array
    image = Image.fromarray(rgb_array, 'RGB')
    
    return image


#NOT EVEN CLOSE TO CORRECT!!!!!!
def contour_map_type1_optimized(df, roll, width):
    num_rows, num_cols = df.shape
    df_array = df.to_numpy()

    # Apply rolling average only if roll > 1
    if roll > 1:
        kernel = np.ones((roll, roll)) / (roll**2)
        df_array = convolve2d(np.pad(df_array, roll//2, mode='edge'), kernel, mode='valid')

    # Convert depths from meters to feet
    df_array *= -3.28084

    # Initialize output image
    pixels = np.full((num_rows, num_cols, 3), (255, 255, 255), dtype='uint8')

    # Define contour bounds
    lower_bounds, upper_bounds = np.arange(5, 500, 5), np.arange(10, 505, 5)

    for lower, upper in zip(lower_bounds, upper_bounds):
        within_range = (df_array >= lower) & (df_array < upper)
        surrounding_outside = (
            within_range &
            ~np.pad(within_range, 1, mode='constant')[1:-1, 1:-1]
        )
        pixels[surrounding_outside] = (0, 0, 0)  # Black for contour lines

    # Heatmap for non-contour points
    non_contour = (pixels[..., 0] == 255) & (pixels[..., 1] == 255) & (pixels[..., 2] == 255)
    if np.any(non_contour):  # Skip if no non-contour points exist
        normalized = (df_array[non_contour] - np.min(df_array)) / (np.ptp(df_array))
        red = (255 * normalized).astype('uint8')
        green_blue = (255 * (1 - normalized)).astype('uint8')
        pixels[non_contour] = np.stack([red, green_blue, green_blue], axis=-1)

    return Image.fromarray(pixels, 'RGB')