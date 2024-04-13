import numpy 
def calculate_profit(a, B1, B2):
    # Calculate the profit for the first bid
    sum_prob1 = sum([a * (x - 900) for x in range(900, B1 - 1)])
    profit1 = (1000 - B1) * sum_prob1
    
    # Calculate the profit for the second bid
    sum_prob2 = sum([a * (x - 900) for x in range(B1, B2 - 1)])
    profit2 = (1000 - B2) * sum_prob2
    
    # Total profit
    total_profit = profit1 + profit2
    
    return total_profit

def cdf(x):
    if x < 900:
        return 0
    elif 900 <= x <= 1000:
        return 0.0001 * (x - 900) ** 2
    else:
        return 1

# Define the function to calculate total expected profit
def expected_profit(b1, b2):
    profit = (1000 - b1) * cdf(b1) + (1000 - b2) * (cdf(b2) - cdf(b1))
    return profit  # Minimize function so use negative profit

def find_best_bids(a):
    max_profit = 0
    best_B1, best_B2 = 0, 0
    for B1 in range(901, 999):
        for B2 in range(B1 + 1, 1000):
            profit = expected_profit(B1, B2)
            if profit > max_profit:
                max_profit = profit
                best_B1, best_B2 = B1, B2
    return best_B1, best_B2, max_profit


# by law of total probality
# 1 = summation from 900 to 1000 of a(x - 900)
# 1 = a * summation from 900 to 1000 of (x - 900)
# 1 = a * summation of 0 to 100 (x)
# 1 = 5050a
a = 1 / 5000.0

best_B1, best_B2, max_profit = find_best_bids(a)
print(f"Best B1: {best_B1}, Best B2: {best_B2}, Maximum Profit: {max_profit}")