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

# shift basket_midprice by a few indices
#lag = -1000
#pivoted_data['basket_midprice_shifted'] = pivoted_data['basket_midprice'].shift(lag)

# pivoted_data['chocolate_midprice'] = 4 * pivoted_data['chocolate_midprice']
# pivoted_data['rose_midprice'] = pivoted_data['rose_midprice']
# pivoted_data['strawberry_midprice'] = 6 * pivoted_data['strawberry_midprice']

# get rid of Na's
# pivoted_data.dropna(inplace=True)

# Save or print your reshaped DataFrame
print(data)

print(len(data))

# get the correlations between variables
correlation_matrix = data[['basket_midprice', 'chocolate_midprice', 'rose_midprice', 'strawberry_midprice']].corr()
print(correlation_matrix)

correlation_matrix = data[['percent_change_basket_midprice_shifted',
                           'percent_change_chocolate_midprice',
                           'percent_change_rose_midprice', 
                           'percent_change_strawberry_midprice']].corr()
print(correlation_matrix)

# graph the prices across time
X = data[['percent_change_chocolate_midprice', 'percent_change_rose_midprice', 'percent_change_strawberry_midprice']]
y = data['percent_change_basket_midprice_shifted']

print(len(X), len(y))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=21)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# print metrics
print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
print("R^2 Score:", r2_score(y_test, y_pred))
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)


plt.figure(figsize=(14, 8))
plt.plot(data['percent_change_basket_midprice'], label='basket')
plt.plot(data[['percent_change_rose_midprice']], label='rose')
plt.plot(data[['percent_change_chocolate_midprice']], label='chocolate')
plt.plot(data[['percent_change_strawberry_midprice']], label='strawberry')
plt.title('Gift Basket Midprice and Product Midprice Changes')
plt.xlabel('Index')
plt.ylabel('Mid_price')
plt.legend()
plt.show()


plt.figure(figsize=(14, 8))
plt.title('Gift Basket Midprice vs Product Midprice Changes')
plt.xlabel('Product Midprice Changes')
plt.ylabel('Basket Midprice Changes')
plt.scatter(data['percent_change_chocolate_midprice'], data['percent_change_basket_midprice'], color='blue', label='chocolate')
#plt.scatter(data['percent_change_rose_midprice'], data['percent_change_basket_midprice'], color='red', label='rose')
#plt.scatter(data['percent_change_strawberry_midprice'], data['percent_change_basket_midprice'], color='green', label='strawberry')
plt.legend()
plt.show()