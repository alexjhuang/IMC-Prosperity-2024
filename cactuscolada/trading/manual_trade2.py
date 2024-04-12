resource_to_index = {
    "pizza": 0,
    "wasabi": 1,
    "snowball": 2,
    "shell": 3
}

matrix = [
    [1, 0.48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, 0.3, 1, 0.46],
    [1.41, 0.61, 2.08, 1]
]

# maximum of five trades
# start with seashells end with seashells

def convert(from_index, to_index):
    return matrix[from_index][to_index]

def execute_trade(trades):
    profit_factor = 1
    start = 3
    end = 3
    for trade in trades:
        end = trade
        profit_factor *= convert(start, end)
        start = end
    return profit_factor * convert(end, 3)


all_possible_middle_trade = []
for i in range(4):
    for j in range(4):
        for k in range(4):
            all_possible_middle_trade.append([i, j, k])


max_profit = 0
max_index = 0
for i, possible_middle_trade in enumerate(all_possible_middle_trade):
    profit_factor = execute_trade(possible_middle_trade)
    if profit_factor > max_profit:
        max_profit = profit_factor
        max_index = i

print("best trade: ", all_possible_middle_trade[max_index])
print("best profit: ", max_profit)