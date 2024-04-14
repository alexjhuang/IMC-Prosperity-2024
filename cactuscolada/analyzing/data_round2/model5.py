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
        return ((60 - humidity) * 0.4)
    elif humidity > 80:
        return ((humidity - 80) * 0.4)
    else:
        return 
    
data['humidity_penalty'] = data['HUMIDITY'].apply(humidity_penalty)
data["change_in_humidity"] = data["humidity_penalty"].diff()
data["next_price"] = data["ORCHIDS"].shift(-1)
print(data.head())

data.dropna(inplace=True)

X = data[["humidity_penalty"]]
y = data["next_price"]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Squared Error:", mse)
print("R² Score:", r2)
print(model.coef_)
print(model.intercept_)