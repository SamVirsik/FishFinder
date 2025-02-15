import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import math
import os

def heat_map_type1(df, width): 
    #(139,69,19)
    #(0,0,0,128)
    colorList = [(0,0,0,50), (212, 255, 1), (190, 255, 1), (166, 255, 17), (139, 255, 17), 
                 (115, 255, 49), (83, 255, 84), (53, 255, 114), (53, 255, 147), (53, 255, 199), 
                 (17, 255, 220), (0, 255, 249), (0, 245, 249), (0, 226, 249), (0, 212, 242), 
                 (0, 198, 242), (0, 182, 242), (0, 167, 242), (0, 150, 242), (0, 128, 242), 
                 (0, 110, 218), (0, 88, 218), (0, 61, 215), (0, 30, 215), (0, 0, 207), (0, 0, 187), 
                 (0, 0, 163), (0, 0, 140), (0, 0, 128), (0, 0, 108), (0, 0, 88)]
    colorList = np.array([i + (255,) if len(i) == 3 else i for i in colorList ])
    len_list = len(colorList)-1

    arr = np.array(df)
    arr *= 3.28084
    arr = (np.abs(arr) - arr)/2
    arr[arr == 0.0] = -1
    arr += 1
    arr = (arr/width).astype(int)
    arr = np.clip(arr,0,len_list)
    arr = colorList[arr]
    img = Image.fromarray(arr.astype('uint8'), 'RGBA')

    # output_name = "img/output_image.png"
    # img.save(output_name)
    # os._exit(0)

    return img

    # number_rows, number_columns = df.shape
    # image = Image.new('RGBA', (number_columns, number_rows), color = (255,255,255,0))
    # pixels = image.load()

    # for row_index, row_data in df.iterrows():
    #     for col_name in df.columns:
    #         mValue = row_data[col_name]
    #         fValue = mValue*3.28084 #foot value
            
    #         heat_map_for_a_point(fValue, width, pixels, row_index, col_name)

    # return image

def heat_map_for_a_point(fValue, width, pixels, r, c):

    colorList = [(139, 69, 19), (212, 255, 1), (190, 255, 1), (166, 255, 17), (139, 255, 17), 
                 (115, 255, 49), (83, 255, 84), (53, 255, 114), (53, 255, 147), (53, 255, 199), 
                 (17, 255, 220), (0, 255, 249), (0, 245, 249), (0, 226, 249), (0, 212, 242), 
                 (0, 198, 242), (0, 182, 242), (0, 167, 242), (0, 150, 242), (0, 128, 242), 
                 (0, 110, 218), (0, 88, 218), (0, 61, 215), (0, 30, 215), (0, 0, 207), (0, 0, 187), 
                 (0, 0, 163), (0, 0, 140), (0, 0, 128), (0, 0, 108), (0, 0, 88)]
    
    scaled = ((abs(fValue)) - fValue) / 2

    if scaled == 0.0:
        pixels[c, r] = colorList[0]
    else:
        scaled = int(scaled/width) + 1
    
    if (scaled > len(colorList)-2):
        pixels[c, r] = colorList[len(colorList)-1]
    else:
        pixels[c, r] = colorList[int(scaled)]
    return pixels

'''
def heat_map_type1_contour(df, width, image): 
    pixels = image.load()
    num_rows, num_cols = df.shape

    colorList = [(139, 69, 19), (212, 255, 1), (190, 255, 1), (166, 255, 17), (139, 255, 17), 
                 (115, 255, 49), (83, 255, 84), (53, 255, 114), (53, 255, 147), (53, 255, 199), 
                 (17, 255, 220), (0, 255, 249), (0, 245, 249), (0, 226, 249), (0, 212, 242), 
                 (0, 198, 242), (0, 182, 242), (0, 167, 242), (0, 150, 242), (0, 128, 242), 
                 (0, 110, 218), (0, 88, 218), (0, 61, 215), (0, 30, 215), (0, 0, 207), (0, 0, 187), 
                 (0, 0, 163), (0, 0, 140), (0, 0, 128), (0, 0, 108), (0, 0, 88)]

    for r in range(num_rows):
        for c in range(num_cols):
            if pixels[c, r] == (255, 255, 255):
                mValue = df.at[r, c]
                fValue = mValue*3.28084 #foot value

                scaled = ((abs(fValue)) - fValue) / 2

                if scaled == 0.0:
                    pixels[c, r] = colorList[0]
                else:
                    scaled = int(scaled/width) + 1
                
                if (scaled > len(colorList)-2):
                    pixels[c, r] = colorList[len(colorList)-1]
                else:
                    pixels[c, r] = colorList[int(scaled)]
    return image
    
'''