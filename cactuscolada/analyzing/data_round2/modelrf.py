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
X = data[['SUNLIGHT', 'HUMIDITY']]  # Features including new rolling sum feature
y = data['ORCHIDS']                         # Target

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = DecisionTreeRegressor(
    random_state=42,
    max_depth=10
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

tree_rules = export_text(model, feature_names=['SUNLIGHT', 'HUMIDITY'], max_depth=30)

with open('tree_rules.txt', 'w') as file:
    file.write(tree_rules)

print("Decision tree rules exported successfully to 'tree_rules.txt'")

from sklearn.tree import _tree

def tree_to_code(tree, feature_names, output_file_path):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    
    with open(output_file_path, 'w') as file:
        file.write("def tree({}):\n".format(", ".join(feature_names)))
    
        def recurse(node, depth):
            indent = "\t" * depth
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                file.write("{}if {} <= {}:\n".format(indent, name, threshold))
                recurse(tree_.children_left[node], depth + 1)
                file.write("{}else:\n".format(indent))
                recurse(tree_.children_right[node], depth + 1)
            else:
                # Adjust the output format for leaf nodes (values)
                values = tree_.value[node]
                # Assuming regression output or binary classification
                prediction = values[0, 0]
                if len(values[0]) > 1:  # Handling classification case
                    prediction = np.argmax(values[0])  
                file.write("{}return {}\n".format(indent, prediction))

        recurse(0, 1)

# Example usage
tree_to_code(model, ['SUNLIGHT', 'HUMIDITY'], 'decision_tree_function.py')

from decision_tree_function import tree

test_predictions = [tree(row['SUNLIGHT'], row['HUMIDITY']) for index, row in X_test.iterrows()]

mae = mean_absolute_error(y_test, test_predictions)
mse = mean_squared_error(y_test, test_predictions)
r2 = r2_score(y_test, test_predictions)

print("Mean Absolute Error on Test Set:", mae)
print("Mean Squared Error on Test Set:", mse)
print("R² Score on Test Set:", r2)