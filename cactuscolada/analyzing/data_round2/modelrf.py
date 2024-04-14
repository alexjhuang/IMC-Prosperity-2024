import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Load data
files = ["prices_round_2_day_-1.csv", "prices_round_2_day_0.csv", "prices_round_2_day_1.csv"]

dataframes = [pd.read_csv(file, delimiter=';') for file in files]
data = pd.concat(dataframes, ignore_index=True)

# Calculate rolling sum of last 10,000 SUNLIGHT data points
data['SUNLIGHT_SUM_10K'] = data['SUNLIGHT'].rolling(window=10000, min_periods=1).sum()

data_filtered = data[data.index > 10000]

# Define features and target
X = data_filtered[['SUNLIGHT', 'HUMIDITY']]  # Features including new rolling sum feature
y = data_filtered['ORCHIDS']                         # Target

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = DecisionTreeRegressor(
    random_state=42,
    max_depth=20,               # Limits the depth of the tree
    min_samples_split=50,      # Requires at least 200 samples to split a node
    min_samples_leaf=30,        # Requires at least 6 samples to form a leaf
    max_leaf_nodes=200          # Maximum number of leaf nodes
)
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

from sklearn.tree import export_text

tree_rules = export_text(model, feature_names=['SUNLIGHT', 'HUMIDITY'])
# print(tree_rules)