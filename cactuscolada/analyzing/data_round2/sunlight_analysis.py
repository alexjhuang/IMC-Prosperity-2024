import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

cutoff = 1980

def humidity_penalty(humidity):
    if humidity < 60:
        return 1 - ((60 - humidity) * 0.004)
    elif humidity > 80:
        return 1 - ((humidity - 80) * 0.004)
    else:
        return 1

# Apply the humidity penalty function
data['Humidity_Penalty'] = data['HUMIDITY'].apply(humidity_penalty)

# Adjust the price of ORCHIDS based on the humidity penalty
data['Adjusted_ORCHIDS'] = data['ORCHIDS'] * data['Humidity_Penalty']

# Determine which records are above the sunlight cutoff
data['Above_Cutoff'] = data['SUNLIGHT'] > cutoff

# Group by 'DAY' to calculate counts and percentages of sunlight above cutoff
results = data.groupby('DAY').agg(
    Total_Count=('Above_Cutoff', 'size'),
    Above_Cutoff_Count=('Above_Cutoff', 'sum')
)

# Calculate the percentage of records above the cutoff and estimate hours above cutoff
results['Percentage_Above_Cutoff'] = (results['Above_Cutoff_Count'] / results['Total_Count']) * 100
results['Hours_Above_Cutoff'] = (results['Above_Cutoff_Count'] / results['Total_Count']) * 12

# Calculate the average price of ORCHIDS for each day
results['Average_Price_ORCHIDS'] = data.groupby('DAY')['Adjusted_ORCHIDS'].mean()

# Display the results including the average price of ORCHIDS
print(results[['Total_Count', 'Above_Cutoff_Count', 'Percentage_Above_Cutoff', 'Hours_Above_Cutoff', 'Average_Price_ORCHIDS']])