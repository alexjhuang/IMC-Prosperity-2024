import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load and process data
files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]
dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

# Define penalties
def humidity_penalty(humidity):
    return 100 - max(0, (humidity - 80) * 0.4) if humidity > 80 else 100 - max(0, (60 - humidity) * 0.4)

def sunlight_penalty(sunlight, cutoff=2500):
    return 100 - ((cutoff - sunlight) / (2500 / 42) * 4) if sunlight < cutoff else 100

# Apply penalties and calculate indexes
data['sunlight_penalty'] = data['SUNLIGHT'].apply(sunlight_penalty)
data['humidity_penalty'] = data['HUMIDITY'].apply(humidity_penalty)
data['Humidity_Index'] = 100 / data['humidity_penalty']
data['Sunlight_Index'] = 100 / data['sunlight_penalty']
data['Production_Index'] = data['Humidity_Index'] * data['Sunlight_Index']

# Prepare data for regression
lag = 10
data['lagged_ORCHIDS'] = data['ORCHIDS'].shift(-lag)
data.dropna(inplace=True)

# Filter data for DAY 1 for testing
test_data = data[data["DAY"] == 1]
X_test = test_data[['Humidity_Index', 'Sunlight_Index', 'Production_Index']]
actual_prices = test_data['lagged_ORCHIDS']

# Train using all other data
train_data = data[data["DAY"] != 1]
X_train = train_data[['Humidity_Index', 'Sunlight_Index', 'Production_Index']]
y_train = train_data['lagged_ORCHIDS']

# Train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict using DAY 1 data
predicted_prices = model.predict(X_test)

print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)
print("R^2 Score:", r2_score(actual_prices, predicted_prices))
print("Mean Squared Error:", mean_squared_error(actual_prices, predicted_prices))

# Plot the results
plt.figure(figsize=(10, 5))
plt.plot(actual_prices.index, actual_prices, label='Actual Prices', color='blue')
plt.plot(actual_prices.index, predicted_prices, label='Predicted Prices', color='red', linestyle='--')
plt.title('Actual vs Predicted Prices for DAY 1')
plt.xlabel('Index')
plt.ylabel('Price')
plt.legend()
plt.show()
