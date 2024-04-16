import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# explore the relationship between prices
files = ["prices_round_3_day_0.csv", "prices_round_3_day_1.csv", "prices_round_3_day_2.csv"]

dataframes = []
for file in files:
    datafile = pd.read_csv(file, delimiter=';')
    
    pivoted_data = datafile.pivot_table(
        index=['day', 'timestamp'], 
        columns='product', 
        values='mid_price', 
        aggfunc='first'
    ).reset_index()

    # Rename columns to make them more descriptive if needed
    pivoted_data.columns = [
        'day',
        'timestamp', 
        'chocolate_midprice',
        'basket_midprice', 
        'rose_midprice', 
        'strawberry_midprice'
    ]

    data['combined_midprice'] = (4 * data['chocolate_midprice']) + data['rose_midprice'] + (6 * data['strawberry_midprice'])
    for product in ['chocolate', 'rose', 'strawberry', 'basket']:
        pivoted_data[f'percent_change_{product}_midprice'] = pivoted_data[f'{product}_midprice'].diff()

    dataframes.append(pivoted_data)

data = pd.concat(dataframes, ignore_index=True)
data.dropna(inplace=True)



