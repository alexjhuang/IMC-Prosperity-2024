import numpy as np
import random
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import HuberRegressor
import math
from sklearn.preprocessing import PolynomialFeatures

def humidity_impact(humidity):
    optimal_range = (60, 80)
    if optimal_range[0] <= humidity <= optimal_range[1]:
        return 1.0  # No change in production
    elif humidity < optimal_range[0]:
        deviation = optimal_range[0] - humidity
    else:
        deviation = humidity - optimal_range[1]
    
    # Calculate compounded production drop
    return 1 - (0.004 * deviation)
    # return np.power(1 - 0.004, deviation)

# Example of calculating the production adjustment for a humidity of 50%
print("Production adjustment for 90% humidity:", humidity_impact(90))

def sunlight_impact(sunlight_data):
    required_lumens = 2500
    timestamp_per_hour = 1_000_000 / 12  # Number of timestamps in one hour
    timestamp_per_ten_minutes = timestamp_per_hour * (10 / 60)  # Number of timestamps in 10 minutes

    # Initialize the deficit count in terms of timestamps
    deficit_timestamps = 0
    minute_penalty = 0.04  # 4% drop every 10 minutes

    # Calculate deficit timestamps
    for lumens in sunlight_data:
        if lumens < required_lumens:
            deficit_timestamps += 100  # Each entry corresponds to 100 timestamps

    # Calculate the number of 10-minute intervals in deficit
    deficit_intervals = deficit_timestamps / timestamp_per_ten_minutes

    # Calculate total production drop
    production_drop = max(0, np.power(1 - minute_penalty, deficit_intervals))

    return production_drop

# Example data: Sunlight readings with timestamps
example_sunlight_data = [
    2400 + (200 * random.randint(0, 10)) for i in range(10000)  # 100 entries with 2400 lumens
]

# Calculate the production adjustment for the example data
adjustment_factor = sunlight_impact(example_sunlight_data)
print("Production adjustment factor:", adjustment_factor)


def process_file(file, window_size, future_index):
    df = pd.read_csv(file, delimiter=';')
    print(df.head())  # Verify data format

    X, y = [], []
    for i in range(window_size, len(df) - future_index):
        current_price = df.loc[i, 'ORCHIDS']
        future_price = df.loc[i + future_index, 'ORCHIDS']
        percentage_change = ((future_price - current_price) / current_price) * 100

        # Calculate sunlight and humidity impacts for the window
        humidity_impacts = humidity_impact(df.loc[i, 'HUMIDITY'])
        sunlight_impacts = sunlight_impact(df.loc[i - window_size:i, 'SUNLIGHT'])
        
        inv_humidity_impacts = 1 / humidity_impacts
        inv_sunlight_impacts = 1 / sunlight_impacts

        # Create the feature vector with the windowed data
        # window_data = df.loc[i - window_size:i - 1]  # Extract the window
        # window_features = window_data.drop(['ORCHIDS'], axis=1).values.flatten()  # Flatten window data, excluding price
        
        # Append impacts to features
        features = [humidity_impacts] 
        poly = PolynomialFeatures(degree=5)
        p_features = np.array([inv_humidity_impacts, inv_sunlight_impacts]).reshape(1, -1)  # Reshape needed for single sample
        poly_features = poly.fit_transform(p_features)
        X.append(features)
        y.append(percentage_change)

    return np.array(X), np.array(y)


window_size = 1
future_index = 100  # Example: Calculate percentage change 10 indices into the future

files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]
train_X, train_y = [], []
test_X, test_y = [], []



# Process the first two files for training data
for file in files[:2]:
    X, y = process_file(file, window_size, future_index)
    train_X.append(X)
    train_y.append(y)

# Process the last file for testing data
test_X, test_y = process_file(files[-1], window_size, future_index)

# Convert list of arrays to a single array and merge training data
train_X = np.vstack(train_X)
train_y = np.concatenate(train_y)

# reshape test data
test_X = np.vstack(test_X)

print("Training Data Shape:", train_X.shape, train_y.shape)
print("Testing Data Shape:", test_X.shape, test_y.shape)

model = LinearRegression()
model.fit(train_X, train_y)

# Make predictions
test_pred = model.predict(test_X)

# Calculate metrics
r2 = r2_score(test_y, test_pred)
mse = mean_squared_error(test_y, test_pred)
print("R-squared:", r2)
print("Mean Squared Error:", mse)
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

import matplotlib.pyplot as plt

# Scatter plot of actual vs. predicted values
plt.figure(figsize=(10, 6))
plt.scatter(test_y, test_pred, alpha=0.5, color='blue')  # Plotting points as scatter plot
plt.title('Actual vs. Predicted Values')
plt.xlabel('Actual ORCHID Prices')
plt.ylabel('Predicted ORCHID Prices')
plt.grid(True)
plt.show()

# Residual plot
plt.figure(figsize=(10, 6))
residuals = test_y - test_pred
plt.scatter(test_pred, residuals, alpha=0.5, color='red')
plt.title('Residual Plot')
plt.xlabel('Predicted ORCHID Prices')
plt.ylabel('Residuals')
plt.axhline(y=0, color='black', linestyle='--')
plt.grid(True)
plt.show()
