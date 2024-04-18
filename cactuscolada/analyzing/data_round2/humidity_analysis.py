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



def humidity_penalty(humidity):
    if humidity < 60:
        return (60 - humidity) * 0.004
    elif humidity > 80:
        return (humidity - 80) * 0.004
    else:
        return 0
    
data['Humidity_Penalty'] = data['HUMIDITY'].apply(humidity_penalty)

bins = [i/100 for i in range(0, 10)]

data['bin'] = pd.cut(data['Humidity_Penalty'], bins=bins, include_lowest=True, right=False)

# Group by 'DAY' and 'bin', then calculate the average 'ORCHIDS' price for each group
grouped_data = data.groupby(['DAY', 'bin'])['ORCHIDS'].mean().reset_index()

# Pivot the data to get separate columns for each 'DAY'
pivot_data = grouped_data.pivot(index='bin', columns='DAY', values='ORCHIDS')

# Plotting the trend lines
fig, ax = plt.subplots(figsize=(10, 6))
pivot_data.plot(kind='line', marker='o', ax=ax)  # 'line' kind with markers at data points
plt.title('Trend Lines of Average Price of ORCHIDS for Each Humidity Bin by Day')
plt.xlabel('Humidity Bin')
plt.ylabel('Average Price of ORCHIDS')
plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend(title='DAY')
plt.show()