import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np

# Read the data from a string, simulating reading from a file
data = pd.read_csv("results.csv", delimiter=';')

# Filter for STARFRUIT only
starfruit_data = data[data['product'] == 'STARFRUIT']['mid_price'].reset_index(drop=True)

# Prepare data for regression model
# Use the previous four prices to predict the next one
X = []
y = []
for i in range(len(starfruit_data) - 4):
    X.append(starfruit_data[i:i+4])
    y.append(starfruit_data[i+4])

X = np.array(X)
y = np.array(y)

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Creating and training the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Use the last four observed prices to make a prediction
last_four_prices = starfruit_data[-4:].values.reshape(1, -1)
next_price_prediction = model.predict(last_four_prices)

print("Predicted next price for STARFRUIT:", next_price_prediction[0])
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)


from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Absolute Error:", mae)
print("Mean Squared Error:", mse)
print("R^2 Score:", r2)