import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

# Function to calculate humidity penalty
def humidity_penalty(humidity):
    if humidity < 60:
        return (60 - humidity) * 0.004
    elif humidity > 80:
        return (humidity - 80) * 0.004
    else:
        return 0

def calculate_sunlight_penalty(data):
    window_size = 100000  # Define the size of the rolling window for sunlight accumulation
    entries_per_window = window_size / 100  # Calculate number of entries per window assuming each entry corresponds to 100 timestamp units

    # Calculate rolling sum (integral) of sunlight over the window
    data['cumulative_sunlight'] = data['SUNLIGHT'].rolling(window=int(entries_per_window), min_periods=1).sum()

    sufficient_sunlight_threshold = 580 * 2500 + 420 * 1000  # Calculate the threshold for sufficient sunlight

    data['penalty'] = (sufficient_sunlight_threshold - data['cumulative_sunlight']).clip(lower=0) * 0.00001

    return data['penalty']

# Apply the penalties
data['Humidity_Penalty'] = data['HUMIDITY'].apply(humidity_penalty)
data['Sunlight_Penalty'] = calculate_sunlight_penalty(data)
data['Total_Penalty'] = data['Humidity_Penalty'] + data['Sunlight_Penalty']

# Calculate the final orchid production
data['Adjusted_Orchid_Production'] = (1 - data['Total_Penalty'])

filtered_data = data[data.index > 10000]

X = filtered_data[['Humidity_Penalty', 'Sunlight_Penalty']]  # Features
y = filtered_data['ORCHIDS']  # Target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Predicted next price for ORCHID:", y_pred[0])
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Calculate metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Absolute Error:", mae)
print("Mean Squared Error:", mse)
print("R^2 Score:", r2)

data.to_csv("combined.csv", sep=';')


# Plotting
plt.figure(figsize=(14, 8))  # Set the figure size

# Plot each penalty and production adjustment
plt.plot(filtered_data['Humidity_Penalty'], label='Humidity Penalty', color='blue', linewidth=2)
plt.plot(filtered_data['Sunlight_Penalty'], label='Sunlight Penalty', color='green', linewidth=2)
# plt.plot(data['Total_Penalty'], label='Total Penalty', color='red', linewidth=2)
# plt.plot(data['Adjusted_Orchid_Production'], label='Adjusted Orchid Production', color='purple', linewidth=2)

# Adding titles and labels
plt.title('Orchid Production Adjustments and Penalties')
plt.xlabel('Index')
plt.ylabel('Values')
plt.legend()  # Show legend

# Show the plot
plt.show()