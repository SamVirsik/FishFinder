import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image

def depth_change_frequency(df):
    num_rows, num_cols = df.shape
    image = Image.new('RGB', (num_cols, num_rows), color = 'white')
    pixels = image.load()

    blank = pd.DataFrame(np.zeros_like(df), index=df.index, columns=df.columns)
    for i in range(1, df.shape[0]):
        for c in range(len(df.columns)):
            try:
                if df.at[i, c] > df.at[i - 1, c]:
                    blank.iloc[i, c] = 1
            except:
                pass
    
    for i in range(1, blank.shape[0]):
        for c in range(len(blank.columns)):
            try:
                if df.at[i, c] >= 0:
                    pixels[c, i] = (139, 69, 19)
                else:
                    count = 0
                    for n in range(np.arange(-1, 2)):
                        for m in range(np.arange(-1, 2)):
                            count += blank.at[i+n, c+m]
                    count = count - blank.at[i, c]

                    g = int(255*(count/8))
                    pixels[c, i] = (g, g, g)
            except:
                pass

    return image