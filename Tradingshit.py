from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
class Derivative:
    def __init__(self):
        self.thearray = np.zeros(1, 3)
    def add_datapoint(self, buy, sell, diff):
        high = buy
        low = sell
        voltrend = diff
        newrow = [high, low, voltrend]
        self.thearray = np.vstack([self.thearray, newrow])
        if len(self.thearray) > 50:
            np.delete(self.thearray, 1, 0)

    def calculate_derivatives(self):
        voltrends = [row[2] for row in self.thearray]
        (summ, numm) = (0, 0)
        for trend in voltrends:
            summ += trend
            numm += 1
        mean = summ/numm
        voltrends.reverse
        dlist = []
        for trend in dlist:
            trend = trend/mean
            if len(dlist) == 0:
                prev = trend
            if len(dlist) > 5:
                if trend-prev-dlist[-1] > 0.5:
                    break
            else:
                dlist.append(trend-prev)
                prev = trend
        (buys, sells) = ([], [])
        for num in range(len(dlist)):
            data = self.thearray[num]
            buys.append(data[0])
            sells.append(data[1])
        buytrend =(buys[0] - buys[-1])/len(buys)
        selltrend =(sells[0] - sells[-1])/len(buys)
        return (buytrend, selltrend)
    def calculate_fair_price(self, position, limit):
        (buytrend, selltrend) = Derivative.calculate_derivatives()
        current_info = self.thearray[-1]
        (buy, sell, voltrend) = current_info
        if voltrend > 0:
            if position > limit/2:
                fair = buy + buytrend
                action = 'Sell'
            else:
                fair = sell
                action = 'Buy'
        else:
            if position > limit/2:
                fair = buy
                action = 'Sell'
            else:
                fair = sell - selltrend
                action = 'Buy'
        return (fair, action, voltrend)








class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():


            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS' or product == 'BANANAS':
                if state.position[product] == KeyError:
                    positiona = 0
                else:
                    positiona= state.position[product]
                    limit = 10

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                Derivative.add_datapoint(max(order_depth.buy_orders.keys()),  min(order_depth.sell_orders.keys()),
                                len(max(order_depth.buy_orders.keys()))-len(min(order_depth.sell_orders.keys())))

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                (acceptable_price, action, voltrend) = Derivative.calculate_fair_price(abs(positiona), limit)
                voltrend = abs(voltrend)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0 and action == 'Buy':

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:

                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    else:
                        print("BUY", str(best_bid_volume) + "x", acceptable_price)
                        orders.append(Order(product, acceptable_price,-voltrend))

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0 and action== 'Sell':
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))
                    else:
                        print("SELL", str(best_bid_volume) + "x", acceptable_price)
                        orders.append(Order(product, acceptable_price,-voltrend))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
