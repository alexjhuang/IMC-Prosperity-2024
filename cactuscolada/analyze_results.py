import pandas as pd

df = pd.read_csv('results1.csv', sep=';')

df['day'] = pd.to_numeric(df['day'])
df['timestamp'] = pd.to_numeric(df['timestamp'])
df['profit_and_loss'] = pd.to_numeric(df['profit_and_loss'])

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

aggregated_results = pd.DataFrame(results)

print("Aggregated Results per Security:")
print(aggregated_results)

total_profit_loss_overall = df['profit_and_loss'].sum()
highest_profit_security = aggregated_results.loc[aggregated_results['Total Profit/Loss'].idxmax()]['Security']

print(f"\nTotal Profit/Loss Across All Securities: {total_profit_loss_overall}")
print(f"Security with the Highest Profit: {highest_profit_security}")