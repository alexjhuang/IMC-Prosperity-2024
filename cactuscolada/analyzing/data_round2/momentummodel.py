import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split

# Simulated or actual stock price data
data = pd.read_csv("prices_round_2_day_-1.csv", delimiter=';')

# Calculate momentum indicators
short_window = 10
long_window = 20

data['short_mavg'] = data['ORCHIDS'].rolling(window=short_window, min_periods=short_window, center=False).mean()
data['long_mavg'] = data['ORCHIDS'].rolling(window=long_window, min_periods=long_window, center=False).mean()

# Create a 'momentum' feature
data['momentum'] = data['short_mavg'] - data['long_mavg']

# Create labels, 1 if the price increased, 0 if it decreased
data['future_return'] = data['ORCHIDS'].shift(-1) - data['ORCHIDS']
data['label'] = np.where(data['future_return'] > 0, 1, 0)

# Drop NaN values
data.dropna(inplace=True)

# Features and labels
X = data[['momentum']]
y = data['label']

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

print("R^2 Score:", r2_score(y_test, y_pred))
print("Mean Squared Error:", mean_squared_error(y_test, y_pred))

