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
    pivoted_data['percent_change_basket_midprice_shifted'] = pivoted_data['basket_midprice_shifted'].diff()

    for product in ['chocolate', 'rose', 'strawberry', 'basket']:
        pivoted_data[f'percent_change_{product}_midprice'] = pivoted_data[f'{product}_midprice'].diff()

    dataframes.append(pivoted_data)

    print("sum of basket midprice changes", pivoted_data['basket_midprice'].diff(1).sum() / pivoted_data['basket_midprice'].iloc[0])
    print("sum of chocolate midprice changes", pivoted_data['chocolate_midprice'].diff(1).sum() /    pivoted_data['chocolate_midprice'].iloc[0])
    print("sum of rose midprice changes", pivoted_data['rose_midprice'].diff(1).sum() / pivoted_data['rose_midprice'].iloc[0])
    print("sum of strawberry midprice changes", pivoted_data['strawberry_midprice'].diff(1).sum() / pivoted_data['strawberry_midprice'].iloc[0])
    #   print difference between first basket midprice and last basket midprice for each day


data = pd.concat(dataframes, ignore_index=True)
data.dropna(inplace=True)

correlation_matrix = data[['percent_change_basket_midprice', 'percent_change_chocolate_midprice']].corr()
print(correlation_matrix)

correlation_matrix = data[['basket_midprice', 'chocolate_midprice']].corr()
print(correlation_matrix)

X = data['chocolate_midprice']
y = data['basket_midprice']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train.values.reshape(-1, 1), y_train)

y_pred = model.predict(X_test.values.reshape(-1, 1))

# model results
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")