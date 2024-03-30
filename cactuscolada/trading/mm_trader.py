from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import List
import json
from typing import Any

class Trader:
    def calculate_current_inventory(self, own_trades, all_products):
        inventory = {product: 0 for product in all_products}  # Initialize all products with 0
        for symbol, trades in own_trades.items():
            for trade in trades:
                # Assuming 'symbol' directly maps to 'product'
                if trade.quantity > 0:
                    inventory[symbol] += trade.quantity
                else:
                    inventory[symbol] += trade.quantity
        return inventory

    def calculate_order_quantity(self, market_liquidity, market_volatility, current_inventory, max_inventory, min_inventory):
        optimal_inventory = (max_inventory + min_inventory) / 2
        inventory_gap = current_inventory - optimal_inventory
        
        base_order_size = market_liquidity * 0.3  # Example: 10% of market liquidity
        volatility_adjustment = max(1, 1 - market_volatility)  # Reduce size in volatile markets
        
        if inventory_gap > 0:
            # Inventory is above optimal, prefer selling
            sell_quantity = base_order_size * volatility_adjustment
            buy_quantity = sell_quantity + inventory_gap  # Buy less if inventory is high
        elif inventory_gap < 0:
            # Inventory is below optimal, prefer buying
            buy_quantity = base_order_size * volatility_adjustment
            sell_quantity = buy_quantity * 0.5  # Sell less if inventory is low
        else:
            # Inventory is optimal, balance buying and selling
            buy_quantity = sell_quantity = base_order_size * volatility_adjustment

        return int(buy_quantity), int(sell_quantity)
    

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                
                # Calculate dynamic spread based on market conditions
                market_spread = best_ask - best_bid
                adjusted_spread = round(max(1, market_spread * 0.2))  # Example of adjusting spread dynamically
                
                # Adjust order prices based on the dynamic spread
                buy_price = best_bid + adjusted_spread
                sell_price = best_ask - adjusted_spread
                
                # Adjust order quantities dynamically (simplified example)
                market_liquidity = 100  # Placeholder
                market_volatility = 0.1  # Placeholder
                current_inventory = self.calculate_current_inventory(state.own_trades, state.listings.keys())[product]
                max_inventory = 20 
                min_inventory = -20 
                
                buy_quantity, sell_quantity = self.calculate_order_quantity(
                    market_liquidity, market_volatility,
                    current_inventory, max_inventory, min_inventory
                )
                buy_quantity, sell_quantity = 10, 10
                
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