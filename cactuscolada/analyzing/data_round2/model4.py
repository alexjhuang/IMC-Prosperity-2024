import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

def humidity_penalty(humidity):
    if humidity < 60:
        return (60 - humidity) * 0.4
    elif humidity > 80:
        return (humidity - 80) * 0.4
    else:
        return 0

def sunlight_penalty(sunlight, cutoff=2500):
    # Convert boolean array to integer by using astype(int), which makes True to 1 and False to 0
    count_above = (sunlight > cutoff).astype(int).sum()
    total_count = len(sunlight)
    percent_above = (count_above / total_count) * 100
    required_percent = 58.333
    if percent_above < required_percent:
        return (required_percent - percent_above) * (4 / 1.3888888899)
    return 0

best_mse = float('inf')

for cutoff in range(2480, 2520):
    # Calculate sunlight penalty using a rolling window of 10,000 timestamps
    data['sunlight_penalty'] = data['SUNLIGHT'].rolling(window=10000, min_periods=10000).apply(
        lambda x: sunlight_penalty(x, cutoff), raw=False
    )
    data['humidity_penalty'] = data['HUMIDITY'].apply(humidity_penalty)


    for lag in range(0, 11400):
        data['lagged_ORCHIDS'] = data['ORCHIDS'].shift(-lag)  # Shift backwards for future prediction

        data['Production_Index'] = 100 - (data['humidity_penalty'] + data['sunlight_penalty'])

        # Filter data to avoid NaNs and use indices after the initial 10,000
        data_filtered = data[(data.index > 10000) & (data.index < len(data) - lag)]

        X = data_filtered[['humidity_penalty', 'sunlight_penalty', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'TRANSPORT_FEES']]  # New feature
        y = data_filtered['lagged_ORCHIDS']  # Lagged price

        # Split and train the model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict and evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        if mse < best_mse:
            best_mse = mse
            print("Cutoff:", cutoff)
            print("Lag:", lag)
            print("Mean Squared Error:", mse)
            print("R² Score:", r2)
            print(model.coef_)
            print(model.intercept_)