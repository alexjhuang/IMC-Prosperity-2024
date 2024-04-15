import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load data
data1 = pd.read_csv('prices_round_2_day_-1.csv', delimiter=';')
data2 = pd.read_csv('prices_round_2_day_0.csv', delimiter=';')
data3 = pd.read_csv('prices_round_2_day_1.csv', delimiter=';')

# Define features and target
features = ['HUMIDITY', 'SUNLIGHT']
target = 'ORCHIDS'


# Combine and prepare training data
train_data = pd.concat([data1, data2])
train_data['PRICE_CHANGE'] = train_data[target].shift(-100) - train_data[target]
train_data.dropna(subset=['PRICE_CHANGE'], inplace=True)  # Drop NaNs after shift calculation


# Prepare feature matrix and target vector for training
X_train, X_val, y_train, y_val = train_test_split(train_data[features], train_data['PRICE_CHANGE'], test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Prepare testing data
data3['PRICE_CHANGE'] = data3[target].shift(-100) - data3[target]
data3.dropna(subset=['PRICE_CHANGE'], inplace=True)  # Ensure no NaNs
X_test = data3[features]
y_test = data3['PRICE_CHANGE']

# Prediction
predicted_change = model.predict(X_test)

# Calculate the future predicted prices and align with the actual future price data
predicted_future_price = data3[target].iloc[:-100].reset_index(drop=True) + predicted_change

# Convert predicted_future_price to a pandas Series with the correct index
predicted_future_price = pd.Series(predicted_future_price, index=data3.index[:-100])

# Actual future prices, aligned by index
actual_future_price = data3[target].shift(-100).dropna()

# Metrics
r2 = r2_score(actual_future_price, predicted_future_price.iloc[actual_future_price.index])
mse = mean_squared_error(actual_future_price, predicted_future_price.iloc[actual_future_price.index])

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(actual_future_price.index, actual_future_price, label='Actual Future Price')
plt.plot(predicted_future_price.index, predicted_future_price, label='Predicted Future Price', linestyle='--')
plt.title('Actual vs Predicted Future Prices')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.legend()
plt.show()

print(f"R-squared: {r2}")
print(f"MSE: {mse}")
