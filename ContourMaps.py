import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
from src.HeatMaps import *
from bisect import bisect_right

def efficient_rolling_and_contours(df, roll, width):
    num_rows, num_cols = df.shape

    # -- 1) Build a NumPy array of the foot values once:
    #      your code does: fValue = df.at[r, c] * -3.28084
    #      We'll do that in bulk:
    foot_array = df.values.astype(float) * -3.28084

    # -- 2) Define lower/upper bounds exactly as in your code:
    lower_bounds = list(range(5, 500, 5))
    upper_bounds = list(range(10, 505, 5))

    # -- 3) Prepare an output array for the final image.
    #      We'll store RGB in a NumPy array and then make a PIL image at the end.
    #      Initialize all pixels to white (255,255,255).
    out_array = np.full((num_rows, num_cols, 3), fill_value=255, dtype=np.uint8)

    # -- 4) Color list for your "heat_map_for_a_point" logic:
    colorList = [
        (139, 69, 19), (212, 255, 1), (190, 255, 1), (166, 255, 17), (139, 255, 17),
        (115, 255, 49), (83, 255, 84), (53, 255, 114), (53, 255, 147), (53, 255, 199),
        (17, 255, 220), (0, 255, 249), (0, 245, 249), (0, 226, 249), (0, 212, 242),
        (0, 198, 242), (0, 182, 242), (0, 167, 242), (0, 150, 242), (0, 128, 242),
        (0, 110, 218), (0, 88, 218), (0, 61, 215), (0, 30, 215), (0, 0, 207),
        (0, 0, 187), (0, 0, 163), (0, 0, 140), (0, 0, 128), (0, 0, 108), (0, 0, 88)
    ]
    colorList = np.array(colorList, dtype=np.uint8)  # shape (31, 3)

    # -- 5) Inline the same heatmap logic you had in heat_map_for_a_point,
    #      except we do not pass in `pixels`; we'll directly set out_array[r,c]:
    def get_heatmap_color(neg_fValue):
        """
        Matches:
           scaled = ((abs(fValue)) - fValue) / 2
           if scaled == 0.0: colorList[0]
           else scaled = int(scaled / width) + 1
                clamp to colorList[-1] if above
        """
        scaled = (abs(neg_fValue) - neg_fValue) / 2.0
        if scaled == 0.0:
            return colorList[0]
        idx = int(scaled / width) + 1
        if idx > (len(colorList) - 2):
            return colorList[-1]
        else:
            return colorList[idx]

    # -- 6) Main loop, EXACT same neighbor logic for contours:
    #       "max_index" is found via bisect rather than a manual loop.
    for r in range(num_rows):
        for c in range(num_cols):
            fValue = foot_array[r, c]

            # find largest index i such that fValue >= lower_bounds[i]
            i = bisect_right(lower_bounds, fValue) - 1  # or None if i < 0

            if i >= 0:
                # is fValue < upper_bounds[i]?
                if fValue < upper_bounds[i]:
                    # within a contour band, check neighbors
                    changed_it = False
                    threshold = upper_bounds[i]
                    for a in range(-1, 2):
                        for b in range(-1, 2):
                            rr = r + a
                            cc = c + b
                            if (0 <= rr < num_rows) and (0 <= cc < num_cols):
                                # if neighbor foot_value > threshold => black
                                if foot_array[rr, cc] > threshold:
                                    out_array[r, c] = (0, 0, 0)  # black
                                    changed_it = True
                                    break
                        if changed_it:
                            break
                    if not changed_it:
                        # if not changed, do the heatmap color
                        # pass -fValue, as in your original call: heat_map_for_a_point(-fValue, ...)
                        out_array[r, c] = get_heatmap_color(-fValue)
                else:
                    # fValue >= upper_bounds[i]
                    out_array[r, c] = get_heatmap_color(-fValue)
            else:
                # i < 0 => fValue < lower_bounds[0]
                out_array[r, c] = get_heatmap_color(-fValue)

    # -- 7) Make a PIL image from out_array and return it
    image = Image.fromarray(out_array, mode='RGB')
    return image
def contour_map_type1(df, roll, width):
    return efficient_rolling_and_contours(df, roll, width)
    num_rows, num_cols = df.shape

    # ROLLING DEPTH VALUES

    #progress print setup, setting up weights for there to be 1 progress print
    roll_operations = roll**2
    total_operations = roll_operations + 1

    rowOnePercent = num_rows/100
    rowNeededToChange = (rowOnePercent/roll_operations)*total_operations
    nextPercent = 1
    print("")
    print("--------------------------")
    
    df_rolled = df.copy()
    for bigRow in range(num_rows):
        for bigCol in range(num_cols):
            myList = []
            for r in range(roll):
                for c in range(roll):
                    rowSub = r-int(roll/2)
                    colSub = c-int(roll/2)
                    try:
                        myList.append(df.at[bigRow+rowSub, bigCol+colSub])
                    except:
                        pass
            length = len(myList)
            totalSum = sum(myList)
            averageValue = totalSum / length
            df_rolled.at[bigRow, bigCol] = averageValue
            
        if(bigRow > rowNeededToChange):
            printString = "Progress: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + (rowOnePercent/roll_operations)*total_operations
            nextPercent +=1
    
    #finalPrint = "Preparing Data: 100%"
    #print('\r' + finalPrint)
            
    #FINDING CONTOUR POINTS
    image = Image.new('RGB', (num_cols, num_rows), color = 'white')
    pixels = image.load()

    #these are the list defining the upper and lower bounds for the contour lines
    #SHOULD BE DONE USING MAX AND MIN TO MAKE THE LOWER AND UPPERBOUNDS
    #lower_bounds = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    #upper_bounds = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

    lower_bounds = list(range(5, 500, 5))
    upper_bounds = list(range(10, 505, 5))

    #progress print stuff
    rowOnePercent = num_rows/100
    rowNeededToChange = rowOnePercent*total_operations

    for r in range(num_rows):
        for c in range(num_cols):
            mValue = df.at[r, c] #meterValues
            fValue = mValue*-3.28084 #foot value

            max_index = None
            for i in range(len(lower_bounds)):
                if fValue >= lower_bounds[i]:
                    max_index = i
            if max_index is not None:
                if fValue < upper_bounds[max_index]:
                    #if we get here it means that our point is within a range we consider reasonable for a contour line
                    #now we need to check that there is a point around it which is outside the range

                    changed_it = False
                    for a in range(-1, 2):
                        for b in range(-1, 2):
                            try:
                                if df.at[r+a, c+b]*-3.28084 > upper_bounds[max_index]:
                                    pixels[c, r] = (0, 0, 0)
                                    changed_it = True
                                    break
                            except: #out of bounds of df
                                pass
                    if not changed_it:
                        pixels = heat_map_for_a_point(-fValue, width, pixels, r, c)
            else:
                pixels = heat_map_for_a_point(-fValue, width, pixels, r, c)
        if(r > rowNeededToChange):
            printString = "Progress: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + rowOnePercent*total_operations
            nextPercent +=1
    finalPrint = "Progress: 100%"
    print('\r' + finalPrint)
    return image

'''
def contour_map_type1_slow(df, roll):
    num_rows, num_cols = df.shape

    rowOnePercent = num_rows/100
    rowNeededToChange = rowOnePercent
    nextPercent = 1
    print("")
    print("--------------------------")
    
    df_rolled = df.copy()
    for bigRow in range(num_rows):
        for bigCol in range(num_cols):
            myList = []
            for r in range(roll):
                for c in range(roll):
                    rowSub = r-int(roll/2)
                    colSub = c-int(roll/2)
                    try:
                        myList.append(df.at[bigRow+rowSub, bigCol+colSub])
                    except:
                        pass
            length = len(myList)
            totalSum = sum(myList)
            averageValue = totalSum / length
            df_rolled.at[bigRow, bigCol] = averageValue
            
        if(bigRow > rowNeededToChange):
            printString = "Preparing Data: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + rowOnePercent
            nextPercent +=1
    
    finalPrint = "Preparing Data: 100%"
    print('\r' + finalPrint)
            
            
    #next 7 lines for progress print:
    df = df_rolled.copy()
    rowOnePercent = num_rows/100
    currentRow = 0
    rowNeededToChange = rowOnePercent
    nextPercent = 1
    
    # 1 foot incraments
    image = Image.new('RGB', (num_cols, num_rows), color = 'white')
    pixels = image.load()
    rowNum = 0
    colNum = 0
    for row in df.values:
        for value in row:
            mValue = df.at[rowNum, colNum] #meterValues
            fValue = mValue*3.28084 #foot value
            if fValue >= 0: #land
                pixels[colNum, rowNum] = (139, 69, 19)
            else:
                myList = []
                try:
                    myList.append((df.at[rowNum-1, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum-1, colNum])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum-1, colNum+1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum, colNum+1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum+1])*3.28084)
                except:
                    pass
                if fValue > -6 and fValue <=-5:
                    for myValue in myList:
                        if myValue>-5:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -20 and fValue <=-15:
                    for myValue in myList:
                        if myValue>-15:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -35 and fValue <=-30:
                    for myValue in myList:
                        if myValue>-30:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -55 and fValue <=-50:
                    for myValue in myList:
                        if myValue>-50:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -75 and fValue <=-70:
                    for myValue in myList:
                        if myValue>-70:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -95 and fValue <=-90:
                    for myValue in myList:
                        if myValue>-90:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -130 and fValue <=-120:
                    for myValue in myList:
                        if myValue>-120:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -175 and fValue <=-150:
                    for myValue in myList:
                        if myValue>-150:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -300 and fValue <=-250:
                    for myValue in myList:
                        if myValue>-250:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -500 and fValue <=-450:
                    for myValue in myList:
                        if myValue>-450:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -900 and fValue <=-800:
                    for myValue in myList:
                        if myValue>-800:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -1200 and fValue <=-1100:
                    for myValue in myList:
                        if myValue>-1100:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -1500 and fValue <=-1400:
                    for myValue in myList:
                        if myValue>-1400:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -1800 and fValue <=-1700:
                    for myValue in myList:
                        if myValue>-1700:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -2000 and fValue <=-1900:
                    for myValue in myList:
                        if myValue>-1900:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -2500 and fValue <=-2400:
                    for myValue in myList:
                        if myValue>-2400:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                else:
                    pass
                    
            colNum+=1
        rowNum+=1
        colNum = 0
        
        #Next 5 lines for progress print:
        if(rowNum > rowNeededToChange):
            printString = "Progress 2: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + rowOnePercent
            nextPercent +=1
    
    finalPrint = "Progress 2: 100%"
    print('\r' + finalPrint)

    return image


    ###### HERE UNTIL THE RETURN STATMENET: 
    
    rowOnePercent = number_rows/100
    currentRow = 0
    rowNeededToChange = rowOnePercent
    nextPercent = 1
    print("--------------------------")
    
    #pair with general:
    rowNum = 0
    colNum = 0
    for row in df.values:
        for value in row:
            if pixels[colNum, rowNum] == (255, 255, 255):
                mValue = df.at[rowNum, colNum] #meterValues
                fValue = mValue*3.28084 #foot value
                if fValue >= 0: #land
                    pixels[colNum, rowNum] = (139, 69, 19)
                elif fValue >= -10:
                    pixels[colNum, rowNum] = (127, 255, 212)
                elif fValue >= -30:
                    pixels[colNum, rowNum] = (64, 224, 208)
                elif fValue >= -60:
                    pixels[colNum, rowNum] = (0, 191, 255)
                elif fValue >= -100:
                    pixels[colNum, rowNum] = (100, 149, 237)
                elif fValue >= -150:
                    pixels[colNum, rowNum] = (30, 144, 255)
                elif fValue >= -200:
                    pixels[colNum, rowNum] = (0, 0, 255)
                elif fValue >= -500:
                    pixels[colNum, rowNum] = (0, 0, 205)
                else:
                    pixels[colNum, rowNum] = (25, 25, 112)
            colNum+=1
        rowNum+=1
        colNum = 0

        #Next 5 lines for progress print:
        if(rowNum > rowNeededToChange):
            printString = "Second Part Progress: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + rowOnePercent
            nextPercent +=1
            
    finalPrint = "Second Part Progress: 100%"
    print('\r' + finalPrint)
    
    return image

def contourMapV1(df, number_rows, number_columns):

    #next 7 lines for progress print:
    rowOnePercent = number_rows/100
    currentRow = 0
    rowNeededToChange = rowOnePercent
    nextPercent = 1
    print("")
    print("--------------------------")
    
    # 1 foot incraments
    image = Image.new('RGB', (number_columns, number_rows), color = 'white')
    pixels = image.load()
    rowNum = 0
    colNum = 0
    for row in df.values:
        for value in row:
            mValue = df.at[rowNum, colNum] #meterValues
            fValue = mValue*3.28084 #foot value
            if fValue >= 0: #land
                pixels[colNum, rowNum] = (139, 69, 19)
            else:
                myList = []
                try:
                    myList.append((df.at[rowNum-1, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum-1, colNum])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum-1, colNum+1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum, colNum+1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum-1])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum])*3.28084)
                except:
                    pass
                try:
                    myList.append((df.at[rowNum+1, colNum+1])*3.28084)
                except:
                    pass
                if fValue > -6 and fValue <=-5:
                    for myValue in myList:
                        if myValue>-5:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -15 and fValue <=-10:
                    for myValue in myList:
                        if myValue>-10:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -20 and fValue <=-15:
                    for myValue in myList:
                        if myValue>-15:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -25 and fValue <=-20:
                    for myValue in myList:
                        if myValue>-20:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -30 and fValue <=-25:
                    for myValue in myList:
                        if myValue>-25:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -35 and fValue <=-30:
                    for myValue in myList:
                        if myValue>-30:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -40 and fValue <=-35:
                    for myValue in myList:
                        if myValue>-35:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -45 and fValue <=-40:
                    for myValue in myList:
                        if myValue>-40:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -50 and fValue <=-45:
                    for myValue in myList:
                        if myValue>-45:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -55 and fValue <=-50:
                    for myValue in myList:
                        if myValue>-50:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -60 and fValue <=-55:
                    for myValue in myList:
                        if myValue>-55:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -65 and fValue <=-60:
                    for myValue in myList:
                        if myValue>-60:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -70 and fValue <=-65:
                    for myValue in myList:
                        if myValue>-65:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -75 and fValue <=-70:
                    for myValue in myList:
                        if myValue>-70:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -80 and fValue <=-75:
                    for myValue in myList:
                        if myValue>-75:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -85 and fValue <=-80:
                    for myValue in myList:
                        if myValue>-80:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -90 and fValue <=-85:
                    for myValue in myList:
                        if myValue>-85:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -95 and fValue <=-90:
                    for myValue in myList:
                        if myValue>-90:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -100 and fValue <=-95:
                    for myValue in myList:
                        if myValue>-95:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -110 and fValue <=-100:
                    for myValue in myList:
                        if myValue>-100:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -120 and fValue <=-110:
                    for myValue in myList:
                        if myValue>-110:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -130 and fValue <=-120:
                    for myValue in myList:
                        if myValue>-120:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -140 and fValue <=-130:
                    for myValue in myList:
                        if myValue>-130:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -150 and fValue <=-140:
                    for myValue in myList:
                        if myValue>-140:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -175 and fValue <=-150:
                    for myValue in myList:
                        if myValue>-150:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -200 and fValue <=-175:
                    for myValue in myList:
                        if myValue>-175:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -225 and fValue <=-200:
                    for myValue in myList:
                        if myValue>-200:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -250 and fValue <=-225:
                    for myValue in myList:
                        if myValue>-225:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -300 and fValue <=-250:
                    for myValue in myList:
                        if myValue>-250:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -350 and fValue <=-300:
                    for myValue in myList:
                        if myValue>-300:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -400 and fValue <=-350:
                    for myValue in myList:
                        if myValue>-350:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -450 and fValue <=-400:
                    for myValue in myList:
                        if myValue>-400:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -500 and fValue <=-450:
                    for myValue in myList:
                        if myValue>-450:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -600 and fValue <=-500:
                    for myValue in myList:
                        if myValue>-500:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -700 and fValue <=-600:
                    for myValue in myList:
                        if myValue>-600:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -800 and fValue <=-700:
                    for myValue in myList:
                        if myValue>-700:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -900 and fValue <=-800:
                    for myValue in myList:
                        if myValue>-800:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                elif fValue > -1000 and fValue <=-900:
                    for myValue in myList:
                        if myValue>-900:
                            pixels[colNum, rowNum] = (0, 0, 0)
                            break
                else:
                    pass
                    
            colNum+=1
        rowNum+=1
        colNum = 0
        
        #Next 5 lines for progress print:
        if(rowNum > rowNeededToChange):
            printString = "Progress: " + str(nextPercent) + "%"
            print('\r' + printString, end='')
            rowNeededToChange = rowNeededToChange + rowOnePercent
            nextPercent +=1
    
    finalPrint = "Progress: 100%"
    print('\r' + finalPrint)
    return image


'''