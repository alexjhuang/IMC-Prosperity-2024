from datamodel import *
from typing import List
import json
from typing import Any
import numpy as np
import collections
from typing import Dict, Tuple

class Trader:
    def __init__(self):
        self.resource_traders: Dict[Symbol, Traitor] = {"AMETHYSTS": AmethystTrader("AMETHYSTS"), "STARFRUIT": StarfruitTrader("STARFRUIT")}
        self.orderManager: OrderManager = OrderManager()

    def run(self, state: TradingState):
        for product in state.position.keys():
            if product == "STARFRUIT":
                continue

            self.resource_traders[product].process(state)
            self.resource_traders[product].trade(self.orderManager)

        traderData = "SAMPLE"
        
        result = self.orderManager.getAllOrders()

        conversions = 1
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    

class OrderManager:
    def __init__(self):
        self.all_orders: Dict[Symbol: list[Order]] = {}
    
    def createOrder(self, product: Symbol, price: int, quantity: int):
        if product not in self.all_orders:
            self.all_orders[product] = []
        self.all_orders[product].append(Order(product, price, quantity))
    
    def getAllOrders(self):
        return self.all_orders
    

class Traitor:
    def __init__(self, symbol: str) -> None:
        self.symbol: str = symbol
        self.product_limit: int = 0
    
    def process(self, state: TradingState) -> None:
        pass

    def trade(self) -> None:
        pass


class StarfruitTrader(Traitor):
    def __init__(self, symbol: str) -> None:
        self.product_limit = 20


class AmethystTrader(Traitor):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 20
        self.acceptable_bid = 10000
        self.acceptable_ask = 10000
        self.position = 0
        self.buy_orders: collections.OrderedDict = None
        self.sell_orders: collections.OrderedDict = None
        self.best_buy_price = 10000
        self.best_ask_price = 10000

    
    def process(self, state: TradingState) -> None:
        self.position = state.position[self.symbol]

        order_depth = state.order_depths[self.symbol]

        self.sell_orders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        self.buy_orders =  collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        self.best_buy_price = next(reversed(self.buy_orders))
        self.best_ask_price = next(reversed(self.sell_orders))


    def trade(self, orderManager: OrderManager):
        current_position = self.position

        # buy underpriced asks
        for ask, volume in self.sell_orders.items():
            if current_position == self.product_limit:
                continue
            
            order_volume = 0
            if ask < self.acceptable_bid:
                order_volume = min(-volume, self.product_limit - current_position)
            elif (self.position < 0 and ask == self.acceptable_bid):
                order_volume = min(-volume, -current_position)
            
            if order_volume != 0:
                current_position += order_volume
                orderManager.append(Order(self.symbol, ask, order_volume))

        undercut_buy = self.best_buy_price + 1
        bid_price = min(undercut_buy, self.acceptable_bid - 1)

        if (current_position < self.product_limit) and (self.position < 0):
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, min(undercut_buy + 1, self.acceptable_bid - 1), num)
            current_position += num

        if (current_position < self.product_limit and (self.position > 15)):
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, min(undercut_buy - 1, self.acceptable_bid - 1), num)
            current_position += num

        if current_position < self.product_limit:
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, bid_price, num)
            current_position += num


        # sell overpriced bids
        current_position = self.position
        undercut_sell = self.best_ask_price - 1
        sell_pr = max(undercut_sell, self.acceptable_ask + 1)

        for bid, volume in self.buy_orders.items():
            if ((bid > self.acceptable_ask) or ((self.position > 0) and (bid == self.acceptable_ask))) and current_position > -self.product_limit:
                order_for = max(-volume, -self.product_limit)
                # order_for is a negative number denoting how much we will sell
                current_position += order_for
                orderManager.createOrder(self.symbol, ask, order_volume)

        if (current_position > -self.product_limit) and (self.position > 0):
            num = max(-40, -self.product_limit- current_position)
            orderManager.createOrder(self.symbol, max(undercut_sell - 1, self.acceptable_ask + 1), num)
            current_position += num

        if (current_position > -self.product_limit) and (self.position < -15):
            num = max(-40, -self.product_limit-current_position)
            orderManager.createOrder(self.symbol, max(undercut_sell + 1, self.acceptable_ask + 1), num)
            current_position += num

        if current_position > -self.product_limit:
            num = max(-40, -self.product_limit-current_position)
            orderManager.createOrder(self.symbol, sell_pr, num)
            current_position += num

        return



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
