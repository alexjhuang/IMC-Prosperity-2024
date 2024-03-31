from datamodel import *
from typing import List
import json
from typing import Any
import numpy as np

class Trader:
    def __init__(self):
        self.price_history = {}  # Track recent trade prices
        self.sma_period = 100  # Example: Calculate SMA over the last 10 prices
        self.max_position = 20

    def update_price_history(self, product, price):
        if product not in self.price_history:
            self.price_history[product] = []
        self.price_history[product].append(price)
        if len(self.price_history[product]) > self.sma_period:
            self.price_history[product].pop(0)
    
    def get_market_trend(self, product, current_price):
        if product not in self.price_history or len(self.price_history[product]) < self.sma_period:
            return 0
        
        prices = self.price_history[product]
        short_term_period = 10
        long_term_period = 50

        if len(prices) < long_term_period:
            return 0

        short_term_ema = self.exponential_moving_average(prices, short_term_period)[-1]
        long_term_ema = self.exponential_moving_average(prices, long_term_period)[-1]

        # Trend strength based on the difference between short and long-term EMAs
        ema_difference = short_term_ema - long_term_ema
        normalized_difference = ema_difference / current_price  # Normalize by the current price for scale

        trend_strength = np.clip(normalized_difference * 10, -1, 1)  # Adjust multiplier as needed for sensitivity

        return trend_strength

    def exponential_moving_average(self, prices, period):
        ema = [sum(prices[:period]) / period]
        multiplier = 2 / (period + 1)
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        return ema
    
    def adjust_inventory_based_on_trend(self, product, current_price):
        market_trend = self.get_market_trend(product, current_price)
        self.update_price_history(product, current_price)
        
        return self.max_position * market_trend

    def get_buy_sell(self, product, position: int, best_bid: int, best_ask: int) -> tuple[int, int, int, int]:
        # Existing setup
        market_spread = best_ask - best_bid
        adjusted_spread = round(max(1, market_spread * 0.2))
        buy_price = best_bid + adjusted_spread
        sell_price = best_ask - adjusted_spread
        max_position = self.max_position
        min_position = -self.max_position
        goal_position = self.adjust_inventory_based_on_trend(product, (best_bid + best_ask) / 2.0)
        logger.print(f"Goal position for {product}: {goal_position}")
        market_volatility = 0.1  # Consider adjusting based on market conditions

        # Adjusting quantities based on the current position and market conditions
        position_gap = position - goal_position
        base_quantity = max(1, abs(int(position_gap * (1 - market_volatility))))

        if position > goal_position:
            buy_quantity = min(base_quantity, max_position - position)
            sell_quantity = min(base_quantity * 2, position - min_position)  # More aggressive if overbought
        elif position < goal_position:
            buy_quantity = min(base_quantity * 2, max_position - position)  # More aggressive if oversold
            sell_quantity = min(base_quantity, position - min_position)
        else:  # Exactly at goal position
            buy_quantity = sell_quantity = base_quantity

        # Preventing order placement that could violate position limits
        if position + buy_quantity > max_position:
            buy_quantity = max(0, max_position - position)
        if position - sell_quantity < min_position:
            sell_quantity = max(0, position - min_position)

        return (buy_price, buy_quantity, sell_price, sell_quantity)

    
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                
                pos = state.position.get(product, 0)
                buy_price, buy_quantity, sell_price, sell_quantity = self.get_buy_sell(product, pos, best_bid, best_ask)
                
                orders.append(Order(product, buy_price, buy_quantity))
                orders.append(Order(product, sell_price, -sell_quantity))
            
            result[product] = orders
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        print(json.dumps([
            self.compress_state(state),
            self.compress_orders(orders),
            conversions,
            trader_data,
            self.logs,
        ], cls=ProsperityEncoder, separators=(",", ":")))

        self.logs = ""

    def compress_state(self, state: TradingState) -> list[Any]:
        return [
            state.timestamp,
            state.traderData,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

logger = Logger()
