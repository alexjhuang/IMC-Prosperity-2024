def calculate_profit(a, b, B1, B2):
    # Calculate the profit for the first bid
    sum_prob1 = sum([a * (x - 900) + b for x in range(900, B1 - 1)])
    profit1 = (1000 - B1) * sum_prob1
    
    # Calculate the profit for the second bid
    sum_prob2 = sum([a * (x - 900) + b for x in range(B1, B2 - 1)])
    profit2 = (1000 - B2) * sum_prob2
    
    # Total profit
    total_profit = profit1 + profit2
    
    return total_profit

def find_best_bids(a, b):
    max_profit = 0
    best_B1, best_B2 = 0, 0
    for B1 in range(901, 999):
        for B2 in range(B1 + 1, 1000):
            profit = calculate_profit(a, b, B1, B2)
            if profit > max_profit:
                max_profit = profit
                best_B1, best_B2 = B1, B2
    return best_B1, best_B2, max_profit

a = 1 / 5050.0
b = 0  # Given value for b

best_B1, best_B2, max_profit = find_best_bids(a, b)
print(f"Best B1: {best_B1}, Best B2: {best_B2}, Maximum Profit: {max_profit}")