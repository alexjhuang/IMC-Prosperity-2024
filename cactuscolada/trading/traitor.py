from datamodel import *
from typing import List
import json
from typing import Any
import numpy as np
import collections
from typing import Dict, Tuple

class Trader:
    def __init__(self):
        self.resource_data: Dict[Symbol: Data] = {"AMETHYSTS": AmethystData("AMETHYSTS"), "STARFRUIT": StarfruitData("STARFRUIT")}
        self.resource_strategies: Dict[Symbol: function] = {"AMETHYSTS": self.tradeAmethyst, "STARFRUIT": self.tradeStarfruit}
        self.orderManager: OrderManager = OrderManager()

    def run(self, state: TradingState):
        for product in state.position.keys():
            self.resource_data[product].update(state)
            self.resource_strategies[product]()

        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        result = self.orderManager.getAllOrders()

        conversions = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    
    def tradeAmethyst(self):
        pass

    def tradeStarfruit(self):
        pass

class Data:
    def __init__(self, symbol: str) -> None:
        self.symbol: str = symbol
        self.product_limit: int = 0
    
    def process(self, state: TradingState) -> None:
        pass


class StarfruitData(Data):
    def __init__(self, symbol: str) -> None:
        self.product_limit = 20


class AmethystData(Data):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 20
        self.acceptable_bid = 10000
        self.acceptable_ask = 10000
        self.buy_orders: collections.OrderedDict = None
        self.sell_orders: collections.OrderedDict = None
    
    def process(self, state: TradingState) -> None:
        order_depth = state.order_depths[self.symbol]

        self.sell_orders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        self.buy_orders =  collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

class OrderManager:
    def __init__(self):
        self.all_orders: Dict[Symbol: list[Order]] = {}
        pass
    
    def createOrder(self, product: Symbol, price: int, quantity: int, is_buy: bool):
        if not is_buy:
            quantity *= -1
        self.all_orders[product].append(Order(product, price, quantity))
    
    def getAllOrders(self):
        return self.all_orders


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
