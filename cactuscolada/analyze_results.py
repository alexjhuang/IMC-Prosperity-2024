import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('results1.csv', sep=';')

df['day'] = pd.to_numeric(df['day'])
df['timestamp'] = pd.to_numeric(df['timestamp'])
df['profit_and_loss'] = pd.to_numeric(df['profit_and_loss'])
df['bid_ask_spread'] = df['ask_price_1'] - df['bid_price_1']

results = []

for security in df['product'].unique():
    security_df = df[df['product'] == security]
    
    total_profit_loss = security_df['profit_and_loss'].sum()
    average_profit_loss = security_df['profit_and_loss'].mean()
    trade_count = security_df.shape[0]
    
    results.append({
        'Security': security,
        'Total Profit/Loss': total_profit_loss,
        'Average Profit/Loss': average_profit_loss,
        'Trade Count': trade_count
    })

for result in results:
    security_df = df[df['product'] == result['Security']]
    
    # Win/Loss Ratio
    wins = security_df[security_df['profit_and_loss'] > 0].shape[0]
    losses = security_df[security_df['profit_and_loss'] <= 0].shape[0]
    win_loss_ratio = wins / losses if losses > 0 else float('inf')  # Avoid division by zero
    result['Win/Loss Ratio'] = win_loss_ratio
    
    # Maximum Drawdown
    cumulative_profit = security_df['profit_and_loss'].cumsum()
    peak = cumulative_profit.cummax()
    drawdown = (peak - cumulative_profit).max()
    result['Maximum Drawdown'] = drawdown

aggregated_results = pd.DataFrame(results)

print("Aggregated Results per Security:")
print(aggregated_results)

total_profit_loss_overall = df['profit_and_loss'].sum()
highest_profit_security = aggregated_results.loc[aggregated_results['Total Profit/Loss'].idxmax()]['Security']

print(f"\nTotal Profit/Loss Across All Securities: {total_profit_loss_overall}")
print(f"Security with the Highest Profit: {highest_profit_security}")

# 1. Profit/Loss Over Time
# Assuming 'timestamp' is a suitable proxy for time
plt.figure(figsize=(10, 6))
for security in df['product'].unique():
    subset = df[df['product'] == security]
    subset['cumulative_profit_loss'] = subset['profit_and_loss'].cumsum()
    plt.plot(subset['timestamp'], subset['cumulative_profit_loss'], label=security)
plt.title('Cumulative Profit/Loss Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Cumulative Profit/Loss')
plt.legend()
plt.show()

# 2. Distribution of Profit/Loss
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='profit_and_loss', hue='product', element='step', fill=False, common_norm=False, palette='bright')
plt.title('Distribution of Profit/Loss per Security')
plt.xlabel('Profit/Loss')
plt.ylabel('Count')
plt.show()

# 3. Win/Loss Ratio per Security
# This requires the win/loss ratio calculations done previously
# Assuming 'aggregated_results' contains this data
plt.figure(figsize=(10, 6))
sns.barplot(data=aggregated_results, x='Security', y='Win/Loss Ratio', palette='bright')
plt.title('Win/Loss Ratio per Security')
plt.xlabel('Security')
plt.ylabel('Win/Loss Ratio')
plt.xticks(rotation=45)
plt.show()

# 4. Maximum Drawdown per Security
plt.figure(figsize=(10, 6))
sns.barplot(data=aggregated_results, x='Security', y='Maximum Drawdown', palette='dark')
plt.title('Maximum Drawdown per Security')
plt.xlabel('Security')
plt.ylabel('Maximum Drawdown')
plt.xticks(rotation=45)
plt.show()

# 5. Bid-Ask Spread Over Time
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='timestamp', y='bid_ask_spread', hue='product')
plt.title('Bid-Ask Spread Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Spread')
plt.show()

# 6. Inventory Levels Over Time
# This plot assumes you have a 'inventory' column representing your inventory level for each security over time
plt.figure(figsize=(12, 6))
for security in df['product'].unique():
    inventory_df = df[df['product'] == security]  # Assuming inventory tracking exists
    plt.plot(inventory_df['timestamp'], inventory_df['inventory'], label=security)
plt.title('Inventory Levels Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Inventory Level')
plt.legend()
plt.show()

# 7. Order Imbalance Over Time
df['order_imbalance'] = (df['bid_volume_1'] - df['ask_volume_1']) / (df['bid_volume_1'] + df['ask_volume_1'])
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='timestamp', y='order_imbalance', hue='product')
plt.title('Order Imbalance Over Time')
plt.xlabel('Timestamp')
plt.ylabel('Order Imbalance')
plt.show()

# 8. Profit/Loss vs. Order Imbalance
plt.figure(figsize=(12, 6))
sns.scatterplot(data=df, x='order_imbalance', y='profit_and_loss', hue='product')
plt.title('Profit/Loss vs. Order Imbalance')
plt.xlabel('Order Imbalance')
plt.ylabel('Profit/Loss')
plt.show()