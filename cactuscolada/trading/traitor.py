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
        self.resource_traders: Dict[Symbol, Traitor] = {
            "AMETHYSTS": AmethystTrader("AMETHYSTS"),
            "STARFRUIT": StarfruitTrader("STARFRUIT"),
            "ORCHIDS": OrchidTrader("ORCHIDS"),
            "GIFT_BASKET": GiftTrader("GIFT_BASKET"),
            "CHOCOLATE": ChocolateTrader("CHOCOLATE"),
            "STRAWBERRIES": StrawberryTrader("STRAWBERRIES"),
            "ROSES": RoseTrader("ROSES"),
        }
        self.orderManager: OrderManager = OrderManager()

    def run(self, state: TradingState):
        if not self.resource_traders:
            self.resource_traders = jsonpickle.decode(state.traderData) # refresh resource traders in case failed.

        for product in self.resource_traders.keys():
            self.resource_traders[product].process(state)
            self.resource_traders[product].trade(self.orderManager)

        traderData = jsonpickle.encode(self.resource_traders) # backup in case AWS messes up and deletes state
        result = self.orderManager.getAllOrders()
        self.orderManager.clearOrders()

        conversions = self.orderManager.conversions
        logger.flush(state, result, conversions, "sample")
        return result, conversions, traderData
    

class OrderManager:
    def __init__(self):
        self.all_orders: Dict[Symbol: list[Order]] = {}
        self.conversions: int = 0
    
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


class GiftItem(Traitor):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 0
        self.position = 0
        self.sell_orders = None
        self.buy_orders = None
        self.best_buy_price = 0
        self.best_ask_price = 0
        self.num_items_in_basket = 0
        self.position = 0
        self.start_basket_price = None
        self.start_chocolate_price = None
        self.start_strawberry_price = None
        self.start_rose_price = None
        self.previous_basket_price = 0
        self.previous_chocolate_price = 0
        self.previous_strawberry_price = 0
        self.previous_rose_price = 0
        self.basket_deviation = 0
        self.chocolate_deviation = 0
        self.strawberry_deviation = 0
        self.rose_deviation = 0
    

    def get_mid_price(self, state: TradingState, symbol: str) -> float:
        sell_orders = collections.OrderedDict(sorted(state.order_depths[symbol].sell_orders.items()))
        buy_orders = collections.OrderedDict(sorted(state.order_depths[symbol].buy_orders.items(), reverse=True))
        best_buy_price = next(reversed(buy_orders))
        best_ask_price = next(reversed(sell_orders))
        return (best_buy_price + best_ask_price) / 2

    
    def process(self, state: TradingState) -> None:
        self.position = state.position.get(self.symbol, 0)
        self.sell_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].sell_orders.items()))
        self.buy_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].buy_orders.items(), reverse=True))
        self.best_buy_price = next(reversed(self.buy_orders))
        self.best_ask_price = next(reversed(self.sell_orders))

        if self.start_basket_price is None:
            self.start_basket_price = self.get_mid_price(state, "GIFT_BASKET")
            self.start_chocolate_price = self.get_mid_price(state, "CHOCOLATE")
            self.start_strawberry_price = self.get_mid_price(state, "STRAWBERRIES")
            self.start_rose_price = self.get_mid_price(state, "ROSES")
        
        for symbol in state.order_depths.keys():
            mid_price = self.get_mid_price(state, symbol)
            if symbol == "CHOCOLATE":
                # if self.previous_chocolate_price == 0:
                #     self.previous_chocolate_price = mid_price
                self.chocolate_deviation = np.log(mid_price / self.start_chocolate_price)
                #self.previous_chocolate_price = mid_price
            elif symbol == "STRAWBERRIES":
                # if self.previous_strawberry_price == 0:
                #     self.previous_strawberry_price = mid_price
                self.strawberry_deviation = np.log(mid_price / self.start_strawberry_price)
                #self.previous_strawberry_price = mid_price
            elif symbol == "ROSES":
                # if self.previous_rose_price == 0:
                #     self.previous_rose_price = mid_price
                self.rose_deviation = np.log(mid_price / self.start_rose_price)
                #self.previous_rose_price = mid_price
            elif symbol == "GIFT_BASKET":
                # if self.previous_basket_price == 0:
                #     self.previous_basket_price = mid_price
                self.basket_deviation = np.log(mid_price / self.start_basket_price)
                #self.previous_basket_price = mid_price

    def expected_price(self):
        pass

    def trade(self, orderManager: OrderManager) -> None:
        expected_price = self.expected_price()
        logger.print("Symbol: ", self.symbol, "Expected Price: ", expected_price, "Midprice: ", (self.best_buy_price + self.best_ask_price) / 2)

        current_position = self.position

        for ask, vol in self.sell_orders.items():
            if (ask < expected_price) and current_position < self.product_limit:
                order_volume = min(-vol, self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, ask, order_volume)
        
        current_position = self.position
        
        for bid, vol in self.buy_orders.items():
            if (bid > expected_price) and current_position > -self.product_limit:
                order_volume = max(-vol, -self.product_limit - current_position)
                current_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)


class ChocolateTrader(GiftItem):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.product_limit = 250
        self.num_items_in_basket = 4
    
    def process(self, state: TradingState) -> None:
        super().process(state)

    def expected_price(self):
        expected_chocolate_deviation = (1.90804964 * self.basket_deviation) + (-0.57008893 * self.strawberry_deviation) + (-0.38161253 * self.rose_deviation) - 0.0002940641867402241
        expected_chocolate_price = self.start_chocolate_price * np.exp(expected_chocolate_deviation)
        return (self.best_ask_price + self.best_buy_price) / 2
    
    def trade(self, orderManager: OrderManager) -> None:
        super().trade(orderManager)


class StrawberryTrader(GiftItem):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.product_limit = 350
        self.num_items_in_basket = 6
    
    def process(self, state: TradingState) -> None:
        super().process(state)

    def expected_price(self):
        expected_strawberry_deviation = (-1.01644375 * self.chocolate_deviation) + (-1.29602731 * self.rose_deviation) + (2.43743794 * self.basket_deviation) + 0.0018273749461782483
        expected_strawberry_price = self.start_strawberry_price * np.exp(expected_strawberry_deviation) / (self.num_items_in_basket)
        return (self.best_ask_price + self.best_buy_price) / 2
    
    def trade(self, orderManager: OrderManager) -> None:
        super().trade(orderManager)
        

class RoseTrader(GiftItem):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.product_limit = 60
        self.num_items_in_basket = 1
    
    def process(self, state: TradingState) -> None:
        super().process(state)
    
    def expected_price(self):
        expected_rose_deviation = (3.98579962 * self.basket_deviation) + (-1.29602731 * self.strawberry_deviation) + (-1.99003957 * self.chocolate_deviation) - 0.0019972956749151373
        expected_rose_price = self.start_rose_price * np.exp(expected_rose_deviation)

        return (self.best_ask_price + self.best_buy_price) / 2

    def trade(self, orderManager: OrderManager) -> None:
        super().trade(orderManager)


class GiftTrader(GiftItem):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)
        self.product_limit = 60
    
    def process(self, state: TradingState) -> None:
        super().process(state)

    def expected_price(self):
        expected_basket_deviation = (0.45610365 * self.chocolate_deviation) + (0.32678862 * self.strawberry_deviation) + (0.18270502 * self.rose_deviation) - 0.00043099352457925955
        expected_basket_price = self.start_basket_price * np.exp(expected_basket_deviation)
        return expected_basket_price

    def trade(self, orderManager: OrderManager) -> None:
        super().trade(orderManager)


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
        self.predicted_price = 0
        self.cache = [None, None, None, None]
        self.coefficients = [-0.00288106, 0.01107265, -0.01295004, 1.00473299]
        self.intercept = 0.02269031575860936
        self.best_buy_price = 0
        self.best_ask_price = 0
        self.acceptable_bid = 0
        self.acceptable_ask = 0
        self.bidPrice = 0
        self.askPrice = 0
        self.humidity = 0
    
    def process(self, state: TradingState) -> None:
        self.bidPrice = state.observations.conversionObservations["ORCHIDS"].bidPrice
        self.askPrice = state.observations.conversionObservations["ORCHIDS"].askPrice
        importTariff = state.observations.conversionObservations["ORCHIDS"].importTariff
        exportTariff = state.observations.conversionObservations["ORCHIDS"].exportTariff
        transportFees = state.observations.conversionObservations["ORCHIDS"].transportFees

        self.adjusted_conversion_ask_price = self.askPrice + importTariff + transportFees
        self.adjusted_conversion_bid_price = self.bidPrice - exportTariff - transportFees

        self.position = state.position.get(self.symbol, 0)

        self.sell_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].sell_orders.items()))
        self.buy_orders = collections.OrderedDict(sorted(state.order_depths[self.symbol].buy_orders.items(), reverse=True))

        self.best_buy_price = next(reversed(self.buy_orders))
        self.best_ask_price = next(reversed(self.sell_orders))
        future_mid_price = self.predict_next_price()
        self.future_adjusted_conversion_bid_price = int(math.floor(future_mid_price - exportTariff - transportFees)) # - (100 * self.stored_fee)))
        self.future_adjusted_conversion_ask_price = int(math.ceil(future_mid_price + importTariff + transportFees))
        self.humidity = state.observations.conversionObservations["ORCHIDS"].humidity

        return
    
    
    def predict_next_price(self):
        prediction = 0
        if None in self.cache:
            prediction = (self.bidPrice + self.askPrice) / 2
        else:
            prediction = self.intercept
            for i, val in enumerate(self.cache):
                prediction += val * self.coefficients[i]

        self.cache = [self.cache[1], self.cache[2], self.cache[3], (self.bidPrice + self.askPrice) / 2]
        # logger.print((self.bidPrice + self.askPrice) / 2, self.cache[2])
        return prediction
    

    def trade(self, orderManager: OrderManager) -> None:
        arbitrage_position = self.position

        for ask, vol in self.sell_orders.items():
            if arbitrage_position < self.product_limit and ask < self.adjusted_conversion_bid_price:
                order_volume = min(-vol, self.product_limit - arbitrage_position)
                arbitrage_position += order_volume
                orderManager.createOrder(self.symbol, ask, order_volume)
        
        for bid, vol in self.buy_orders.items():
            if arbitrage_position > -self.product_limit and bid > self.adjusted_conversion_ask_price:
                # logger.print(self.humidity, self.adjusted_conversion_ask_price, bid)
                order_volume = max(-vol, -self.product_limit - arbitrage_position)
                arbitrage_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)

        orderManager.createConversion(self.position)
        return
    
    def trade2(self, orderManager: OrderManager) -> None:
        current_position = self.position
        real_position = self.position

        for ask, vol in self.sell_orders.items():
            if (ask < self.adjusted_conversion_bid_price) and current_position < self.product_limit:
                order_volume = min(-vol, self.product_limit - current_position)
                real_position += order_volume
                current_position += order_volume
                orderManager.createOrder(self.symbol, ask, order_volume)

        if current_position < self.product_limit:
            num = self.product_limit - current_position
            orderManager.createOrder(self.symbol, self.future_adjusted_conversion_ask_price + 3, num)
            current_position += num
        
        current_position = self.position
        
        for bid, vol in self.buy_orders.items():
            if (bid > self.adjusted_conversion_ask_price) and current_position > -self.product_limit:
                order_volume = max(-vol, -self.product_limit - current_position)
                real_position += order_volume
                current_position += order_volume
                orderManager.createOrder(self.symbol, bid, order_volume)

        if current_position > -self.product_limit:
            num = -self.product_limit - current_position
            orderManager.createOrder(self.symbol, self.future_adjusted_conversion_bid_price - 3, num)
        
        orderManager.createConversion(self.position)


class StarfruitTrader(Traitor):
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.product_limit = 20
        self.position = 0
        self.cache = [None, None, None, None]
        self.coefficients = [0.18925881, 0.20729211, 0.26096944, 0.3419978]
        self.intercept = 2.088673614521994
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
