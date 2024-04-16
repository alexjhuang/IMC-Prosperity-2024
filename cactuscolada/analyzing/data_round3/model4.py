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

    lag = -1
    pivoted_data['basket_midprice_shifted'] = pivoted_data['basket_midprice'].shift(lag)
    pivoted_data['percent_change_basket_midprice_shifted'] = pivoted_data['basket_midprice_shifted'].pct_change()

    for product in ['chocolate', 'rose', 'strawberry', 'basket']:
        pivoted_data[f'percent_change_{product}_midprice'] = pivoted_data[f'{product}_midprice'].pct_change()

    dataframes.append(pivoted_data)

data = pd.concat(dataframes, ignore_index=True)
data.dropna(inplace=True)

data['combined_midprice'] = (4 * data['chocolate_midprice']) + data['rose_midprice'] + (6 * data['strawberry_midprice'])

plt.figure(figsize=(14, 8))
plt.plot(data[['percent_change_basket_midprice']], label='basket')
plt.plot(data[['percent_change_chocolate_midprice']], label='chocolate')
plt.title('Gift Basket Midprice and Product Midprice Changes')
plt.xlabel('Index')
plt.ylabel('Mid_price')
plt.legend()
plt.show()

# get the correlations between variables
correlation_matrix = data[['basket_midprice', 'chocolate_midprice', 'rose_midprice', 'strawberry_midprice']].corr()
print(correlation_matrix)

correlation_matrix = data[['percent_change_basket_midprice',
                           'percent_change_chocolate_midprice',
                           'percent_change_rose_midprice', 
                           'percent_change_strawberry_midprice']].corr()
print(correlation_matrix)

print(data['percent_change_basket_midprice'].describe().loc[['min', '25%', '50%', '75%', 'max']])
print(data['percent_change_chocolate_midprice'].describe().loc[['min', '25%', '50%', '75%', 'max']])

import seaborn as sns
plt.figure(figsize=(10, 6))

# Overlaying histograms
sns.histplot(data['percent_change_basket_midprice'], bins=30, kde=True, color='blue', alpha=0.6, label='Basket Midprice % Change')
sns.histplot(data['percent_change_chocolate_midprice'], bins=30, kde=True, color='red', alpha=0.6, label='Chocolate Midprice % Change')

# Add title and labels
plt.title('Overlayed Distribution of Percentage Changes')
plt.xlabel('Percentage Change')
plt.ylabel('Frequency')

# Add legend to differentiate the distributions
plt.legend()

# Show the plot
plt.show()