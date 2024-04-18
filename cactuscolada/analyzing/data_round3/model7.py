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

    pivoted_data['combined_midprice'] = (4 * pivoted_data['chocolate_midprice']) + pivoted_data['rose_midprice'] + (6 * pivoted_data['strawberry_midprice'])
    for product in ['chocolate', 'rose', 'strawberry', 'basket', 'combined']:
        pivoted_data[f'change_{product}_midprice'] = pivoted_data[f'{product}_midprice'].diff()
    
    for product in ['chocolate', 'rose', 'strawberry', 'basket', 'combined']:
        pivoted_data[f'log_change_{product}_midprice'] = np.log(pivoted_data[f'{product}_midprice'] / pivoted_data[f'{product}_midprice'].iloc[0])
        # pivoted_data[f'log_change_{product}_midprice'] = np.log(pivoted_data[f'{product}_midprice'] / pivoted_data[f'{product}_midprice'].shift(1))

    # print basket total log change
    # print("basket total log change", np.log(pivoted_data['basket_midprice'].iloc[-1] / pivoted_data['basket_midprice'].iloc[0]))
    # print("combined total log change", np.log(pivoted_data['combined_midprice'].iloc[-1] / pivoted_data['combined_midprice'].iloc[0]))

    dataframes.append(pivoted_data)

data = pd.concat(dataframes, ignore_index=True)
data.dropna(inplace=True)

# print("basket total log change", np.log(data['basket_midprice'].iloc[-1] / data['basket_midprice'].iloc[0]))
# print("combined total log change", np.log(data['combined_midprice'].iloc[-1] / data['combined_midprice'].iloc[0]))

correlation_matrix = data[['log_change_basket_midprice', 'log_change_combined_midprice']].corr()
print(correlation_matrix)

correlation_matrix = data[['log_change_basket_midprice', 'log_change_chocolate_midprice', 'log_change_strawberry_midprice', 'log_change_rose_midprice']].corr()
print(correlation_matrix)

X = data[['log_change_strawberry_midprice', 'log_change_chocolate_midprice', 'log_change_basket_midprice']]
y = data['log_change_rose_midprice']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=21)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# model results
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print("MSE:", mse)
print("R2:", r2)
print("model coefficients:", model.coef_)
print("model intercept:", model.intercept_)


plt.figure(figsize=(10, 7))
plt.plot(data['log_change_chocolate_midprice'], label='chocolate', color='orange')
plt.plot(data['log_change_basket_midprice'], label='basket')
plt.yscale('linear')
plt.xscale('linear')
plt.show()