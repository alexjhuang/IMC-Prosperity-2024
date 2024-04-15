import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# explore the relationship between prices
files = ["prices_round_3_day_0.csv", "prices_round_3_day_1.csv", "prices_round_3_day_2.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)
data = data[['timestamp', 'product', 'mid_price']]
# flatten data so the mid_price of each product is in a separate column with timstep as the index
data = data.pivot(columns='product', values='mid_price')
print(data.head())

# get the correlations between variables
correlation_matrix = data.corr()
print(correlation_matrix)

# graph the prices across time
