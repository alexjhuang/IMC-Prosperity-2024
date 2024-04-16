import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

price_files = ["prices_round_3_day_0.csv", "prices_round_3_day_1.csv", "prices_round_3_day_2.csv"]
trade_files = ["trades_round_3_day_0_nn.csv", "trades_round_3_day_1_nn.csv", "trades_round_3_day_2_nn.csv"]

dataframes = []
flatframes = []
for file in price_files:
    datafile = pd.read_csv(file, delimiter=';')
    
    pivoted_data = datafile.pivot_table(
        index=['day', 'timestamp'], 
        columns='product', 
        values='mid_price', 
        aggfunc='first'
    ).reset_index()

    # Rename columns to make them more descriptive if needed
    pivoted_data.columns = [
        'day',
        'timestamp', 
        'chocolate_midprice',
        'basket_midprice', 
        'rose_midprice', 
        'strawberry_midprice'
    ]

    dataframes.append(pivoted_data)
    flatframes.append(datafile)

price_data = pd.concat(dataframes, ignore_index=True)
print(price_data)
print(len(price_data))

flat_data = pd.concat(flatframes, ignore_index=True)

tradeframes = []
for i, file in enumerate(trade_files):
    datafile = pd.read_csv(file, delimiter=';')
    datafile['day'] = i
    
    pivoted_data = datafile.pivot_table(
        index=['day', 'timestamp'], 
        columns='symbol', 
        values=['price', 'quantity'], 
        aggfunc='first'
    ).reset_index()

    tradeframes.append(datafile)

trade_data = pd.concat(tradeframes, ignore_index=True)
print(trade_data)
print(len(trade_data))
# data = pd.merge(prices, trades, how='left', left_on=['timestamp', 'product'], right_on=['timestamp', 'symbol'])


# graph of mid prices and trades of strawberry per timestamp
strawberry_data = trade_data[trade_data['symbol'] == 'STRAWBERRIES']
strawberry_prices = flat_data[flat_data['product'] == 'STRAWBERRIES']

plt.figure(figsize=(14, 8))
plt.plot(strawberry_prices['timestamp'], strawberry_prices['bid_price_1'], label='strawberry best bid')
plt.plot(strawberry_prices['timestamp'], strawberry_prices['ask_price_1'], label='strawberry best ask')
plt.plot(strawberry_prices['timestamp'], strawberry_prices['mid_price'], label='strawberry mid price')
plt.scatter(strawberry_data['timestamp'], strawberry_data['price'], s=strawberry_data['quantity'] * 5, c='red', label='trades')
plt.title('Strawberry Midprice and Trade Quantity')
plt.xlabel('Timestamp')
plt.ylabel('Mid_price')
plt.legend()
plt.show()