import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Load data
files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

def humidity_penalty(humidity):
    if humidity < 60:
        return 1 - ((60 - humidity) * 0.004)
    elif humidity > 80:
        return 1 - ((humidity - 80) * 0.004)
    else:
        return 1
    
data['Humidity_Penalty'] = data['HUMIDITY'].apply(humidity_penalty)

cutoff = 2600
data['Above_Cutoff'] = (data['SUNLIGHT'] > cutoff).astype(int)
data['Count_Above_Cutoff_10K'] = data['Above_Cutoff'].rolling(window=10000, min_periods=1).sum()
data['Percentage_Above_Cutoff_10K'] = (data['Count_Above_Cutoff_10K'] / 10000) * 100

cutoff_ratio = 7/12 * 100  # Convert the fraction to a percentage

def adjust_value(row):
    if row['Percentage_Above_Cutoff_10K'] >= cutoff_ratio:
        return 1
    else:
        percent_diff = cutoff_ratio - row['Percentage_Above_Cutoff_10K']
        adjustment = 1 - (percent_diff * 0.004)
        return adjustment

data['Adjusted_Value'] = data.apply(adjust_value, axis=1)
data['inverse_adjusted_value'] = 1 / data['Adjusted_Value']

data["Production"] = data['Humidity_Penalty']
data["inverse_production"] = 1 / data["Production"]

data['SUNLIGHT_SUM_10K'] = data['SUNLIGHT'].rolling(window=10000, min_periods=1).sum()

data_filtered = data[data.index > 10000]

# Define features and target
X = data_filtered[['Humidity_Penalty', 'SUNLIGHT_SUM_10K']]  # Features including new rolling sum feature
y = data_filtered['ORCHIDS']                         # Target

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Absolute Error:", mae)
print("Mean Squared Error:", mse)
print("R² Score:", r2)
