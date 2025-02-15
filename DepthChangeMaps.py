import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image

def depth_change_downward(df):
    df_new = pd.DataFrame(False, index=df.index, columns=df.columns)

    num_rows, num_cols = df.shape
    image = Image.new('RGB', (num_cols, num_rows), color = 'white')
    pixels = image.load()

    for i in range(1, df.shape[0]):
        for col in df.columns:
            try:
                if df.at[i, col] >= 0:
                    pixels[col, i] = (139, 69, 19)
                elif df.at[i, col] > df.at[i - 1, col]:
                    pixels[col, i] = (0, 0, 0)
            except:
                pass

    return image



def depth_change(df):
    '''
    Plots black as downward depth increase, and white as the same or decrease. 
    For texture. 
    '''
    num_rows, num_cols = df.shape
    image = Image.new('RGB', (num_cols, num_rows), color='white')
    pixels = image.load()

    # Create a blank DataFrame to track the downward increases
    blank = pd.DataFrame(np.zeros_like(df), index=df.index, columns=df.columns)

    # Detect downward increases (1 if the depth decreases, otherwise 0)
    blank.iloc[1:] = (df.iloc[1:].values < df.iloc[:-1].values).astype(int)

    # Convert the blank DataFrame to an image
    for i in range(1, num_rows):
        for c in range(num_cols):
            if df.at[i, c] >= 0:  # Land areas
                pixels[c, i] = (139, 69, 19)  # Brown for land
            elif blank.at[i, c] == 1:  # Depth decreased (downward change)
                pixels[c, i] = (255, 255, 255)  
            else:  # Depth increased or no change
                pixels[c, i] = (0, 0, 0) 

    return image


def depth_change_frequency(df):
    '''
    Makes a grayscale image for which the intensity of gray is based on 
    the number of surrounding pixels for which there was a downward 
    depth decrease. 
    '''
    num_rows, num_cols = df.shape
    image = Image.new('RGB', (num_cols, num_rows), color='white')
    pixels = image.load()

    # Create a blank DataFrame to track the downward increases
    blank = pd.DataFrame(np.zeros_like(df), index=df.index, columns=df.columns)

    # Detect downward increases (1 if the depth decreases, otherwise 0)
    blank.iloc[1:] = (df.iloc[1:].values < df.iloc[:-1].values).astype(int)

    # Count the surrounding downward increases in the 3x3 neighborhood
    for i in range(1, num_rows):
        for c in range(num_cols):
            if df.iloc[i, c] >= 0:
                # Default pixel color (brown)
                pixels[c, i] = (139, 69, 19)
            else:
                # Count downward changes in the neighborhood (8 neighbors)
                count = 0
                for n in range(-1, 2):
                    for m in range(-1, 2):
                        if 0 <= i + n < num_rows and 0 <= c + m < num_cols:
                            count += blank.at[i + n, c + m]
                # Avoid counting the current cell
                count -= blank.at[i, c]
                
                # Grayscale value based on count (scaled to [0, 255])
                g = int(255 * (count / 8))
                pixels[c, i] = (g, g, g)

    return image