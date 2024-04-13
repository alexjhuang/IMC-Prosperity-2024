from datamodel import *
import json
from typing import Any
import numpy as np
import math
import collections
from typing import Dict, Tuple, List
import jsonpickle


class Trader:
    def __init__(self):
        self.resource_traders: Dict[Symbol, Traitor] = {"AMETHYSTS": AmethystTrader("AMETHYSTS"), "STARFRUIT": StarfruitTrader("STARFRUIT"), "ORCHIDS": OrchidTrader("ORCHIDS")}
        self.orderManager: OrderManager = OrderManager()

    def run(self, state: TradingState):
        if not self.resource_traders:
            self.resource_traders = jsonpickle.decode(state.traderData) # refresh resource traders in case failed.

        for product in self.resource_traders.keys():
            self.resource_traders[product].process(state)
            self.resource_traders[product].trade(self.orderManager)

        # traderData = jsonpickle.encode(self.resource_traders) # backup in case AWS messes up and deletes state
        traderData = "sample"
        result = self.orderManager.getAllOrders()
        self.orderManager.clearOrders()
        conversions = self.orderManager.conversions

        logger.print(self.orderManager.orchid_pnl)
        logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    

class OrderManager:
    def __init__(self):
        self.all_orders: Dict[Symbol: list[Order]] = {}
        self.conversions: int = 0
        self.orchid_pnl = 0
    
    def createConversion(self, position: int):
        self.conversions = -position
    
    def createOrder(self, product: Symbol, price: int, quantity: int):
        if product not in self.all_orders:
            self.all_orders[product] = []
        self.all_orders[product].append(Order(product, price, quantity))
    
    def getAllOrders(self):
        return self.all_orders

    def clearOrders(self):
        self.all_orders = {}
    

class Traitor:
    def __init__(self, symbol: str) -> None:
        self.symbol: str = symbol
        self.product_limit: int = 0
    
    def process(self, state: TradingState) -> None:
        pass

    def trade(self, orderManager: OrderManager) -> None:
        pass


class OrchidTrader(Traitor):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 100
        self.position = 0
        self.adjusted_conversion_ask_price = 0
        self.adjusted_conversion_bid_price = 0
        self.stored_fee = 0.1 # per 1 unit long per timestamp
        self.sell_orders = None
        self.buy_orders = None
    
    def process(self, state: TradingState) -> None:
        bidPrice = state.observations.conversionObservations["ORCHIDS"].bidPrice
        askPrice = state.observations.conversionObservations["ORCHIDS"].askPrice
        importTariff = state.observations.conversionObservations["ORCHIDS"].importTariff
        exportTariff = state.observations.conversionObservations["ORCHIDS"].exportTariff
        transportFees = state.observations.conversionObservations["ORCHIDS"].transportFees

        self.adjusted_conversion_ask_price = askPrice + importTariff + transportFees
        self.adjusted_conversion_bid_price = bidPrice - exportTariff - transportFees

        self.position = state.position.get(self.symbol, 0)

        self.sell_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].sell_orders.items()))
        self.buy_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].buy_orders.items(), reverse=True))

        return

    def trade(self, orderManager: OrderManager) -> None:
        current_position = self.position # should be 0

        for ask, vol in self.sell_orders.items():
            if current_position < self.product_limit and ask < self.adjusted_conversion_bid_price:
                order_volume = min(-vol, self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, ask, order_volume)
                # print pnl
                orderManager.orchid_pnl += (self.adjusted_conversion_bid_price - ask) * order_volume
        
        for bid, vol in self.buy_orders.items():
            if current_position > -self.product_limit and bid > self.adjusted_conversion_ask_price:
                order_volume = max(-vol, -self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)
                # print pnl
                orderManager.orchid_pnl += (bid - self.adjusted_conversion_ask_price) * order_volume
                

        orderManager.createConversion(current_position)

        return None


class StarfruitTrader(Traitor):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 20
        self.position = 0
        self.cache = [None, None, None, None]
        self.coefficients = [0.18836653, 0.20711758, 0.26145864, 0.34260796]
        self.intercept = 2.2675006548934107
        self.sell_orders = None
        self.buy_orders = None
        self.best_buy_price = 0
        self.best_ask_price = 0
        self.acceptable_bid = 0
        self.acceptable_ask = 0
    
    def process(self, state: TradingState) -> None:
        self.position = state.position.get(self.symbol, 0)
        self.sell_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].sell_orders.items()))
        self.buy_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].buy_orders.items(), reverse=True))
        self.best_buy_price = next(reversed(self.buy_orders))
        self.best_ask_price = next(reversed(self.sell_orders))
        mid_price = self.predict_next_price()
        self.acceptable_bid = int(math.floor(mid_price)) - 1
        self.acceptable_ask = int(math.ceil(mid_price)) + 1


    def predict_next_price(self):
        prediction = 0
        if None in self.cache:
            prediction = (self.best_ask_price + self.best_buy_price) / 2
        else:
            prediction = self.intercept
            for i, val in enumerate(self.cache):
                prediction += val * self.coefficients[i]

        self.cache = [self.cache[1], self.cache[2], self.cache[3], (self.best_ask_price + self.best_buy_price) / 2]
        logger.print((self.best_ask_price + self.best_buy_price) / 2, prediction)
        print(self.sell_orders, self.best_ask_price)
        print(self.buy_orders, self.best_buy_price)
        return prediction
    

    def trade(self, orderManager: OrderManager) -> None:
        current_position = self.position

        for ask, vol in self.sell_orders.items():
            if ((ask <= self.acceptable_bid) or ((self.position < 0) and (ask == self.acceptable_bid + 1))) and current_position < self.product_limit:
                order_volume = min(-vol, self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, ask, order_volume)

        bid_price = min(self.best_buy_price + 1, self.acceptable_bid) 

        if current_position < self.product_limit:
            num = self.product_limit - current_position
            orderManager.createOrder(self.symbol, bid_price, num)
            current_position += num
        
        current_position = self.position
        
        for bid, vol in self.buy_orders.items():
            if ((bid >= self.acceptable_ask) or ((self.position > 0) and (bid + 1 == self.acceptable_ask))) and current_position > -self.product_limit:
                order_volume = max(-vol, -self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)

        
        sell_price = max(self.best_ask_price - 1, self.acceptable_ask)

        if current_position > -self.product_limit:
            num = -self.product_limit - current_position
            orderManager.createOrder(self.symbol, sell_price, num)


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
        self.position = state.position.get(self.symbol, 0)

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
                orderManager.createOrder(self.symbol, ask, order_volume)

        undercut_buy = self.best_buy_price + 1
        bid_price = min(undercut_buy, self.acceptable_bid - 1)

        if (current_position < self.product_limit) and (self.position < 0): # give better bids, we need to get back to 0
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, min(undercut_buy + 1, self.acceptable_bid - 1), num)
            current_position += num

        if (current_position < self.product_limit and (self.position > 15)): # chill on buying, our position too positive
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, min(undercut_buy - 1, self.acceptable_bid - 1), num)
            current_position += num

        if current_position < self.product_limit: # in between, life as usual
            num = min(40, self.product_limit - current_position)
            orderManager.createOrder(self.symbol, bid_price, num)
            current_position += num


        # sell to overpriced bids
        current_position = self.position
        undercut_sell = self.best_ask_price - 1
        sell_pr = max(undercut_sell, self.acceptable_ask + 1)
        
        for bid, volume in self.buy_orders.items():
            if current_position == -self.product_limit:
                continue
            
            order_volume = 0
            if bid > self.acceptable_ask:
                order_volume = max(-volume, -self.product_limit)
            elif (self.position > 0) and (bid == self.acceptable_ask):
                order_volume = max(-volume, -self.product_limit)
            
            if order_volume != 0:
                current_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)

        if (current_position > -self.product_limit) and (self.position > 0): # give better asks, we need to get back to 0
            num = max(-40, -self.product_limit - current_position)
            orderManager.createOrder(self.symbol, max(undercut_sell - 1, self.acceptable_ask + 1), num)
            current_position += num

        if (current_position > -self.product_limit) and (self.position < -15): # chill on selling, our position too negative
            num = max(-40, -self.product_limit - current_position)
            orderManager.createOrder(self.symbol, max(undercut_sell + 1, self.acceptable_ask + 1), num)
            current_position += num

        if current_position > -self.product_limit: # in between, life as usual
            num = max(-40, -self.product_limit - current_position)
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
