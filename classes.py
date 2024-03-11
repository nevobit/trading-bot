import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, time
import pytz

class Bot:
    def __init__(self,symbol,volume,profit_target,no_of_safty_orders,direction, timeframes):
        self.symbol = symbol
        self.volume = volume
        self.profit_target = profit_target
        self.no_of_safty_orders = no_of_safty_orders
        self.direction = direction
        self.win_count = 0
        self.timeframes = timeframes
        self.daily_entries = []  # Lista para almacenar las entradas diarias
        self.transactions = []
        #self.ny_tz = pytz.timezone('America/New_York')

    def is_trading_day(self):
        today = datetime.today().weekday()
        return today >= 1 and today <= 4

    def check_profit_loss(self, symbol):
        current_profit = self.cal_profit(symbol)
        if current_profit >= self.profit_target or current_profit <= -15:  # 30 pips de ganancia, 15 pips de pérdida
            self.close_all(symbol)

    def market_order(self,symbol, volume, order_type):
        tick = mt5.symbol_info_tick(symbol)
        order_dict = {'buy': 0, 'sell': 1}
        price_dict = {'buy': tick.ask, 'sell': tick.bid}

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_dict[order_type],
            "price": price_dict[order_type],
            "deviation": 20,
            "magic": 100,
            "comment": "python market order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        order_result = mt5.order_send(request)
        print(order_result)

        return order_result

    def cal_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        profit = float(df["profit"].sum())
        return profit

    def cal_volume(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        profit = float(df["volume"].sum())
        return profit

    def cal_buy_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 0]
        profit = float(df["profit"].sum())
        return profit

    def cal_sell_profit(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 1]
        profit = float(df["profit"].sum())
        return profit

    def cal_buy_margin(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 0]

        sum = 0
        for i in df.index:
            volume = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, volume, open_price)
            sum += margin
        return sum

    def cal_sell_margin(self,symbol):
        usd_positions = mt5.positions_get(symbol=symbol)
        df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        df = df.loc[df.type == 1]

        sum = 0
        for i in df.index:
            volume = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_SELL, symbol, volume, open_price)
            sum += margin
        return sum

    def cal_pct_profit(self,symbol):
        total_profit = self.cal_profit(symbol)
        buy_margin = self.cal_buy_margin(symbol)
        sell_margin = self.cal_sell_margin(symbol)
        total_margin = buy_margin + sell_margin
        pct_profit = (total_profit / total_margin) * 100
        return pct_profit

    def close_position(self,position):
        tick = mt5.symbol_info_tick(position.symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": 20,
            "magic": 100,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result

    def close_all(self,symbol):
        position = mt5.positions_get(symbol=symbol)
        for position in position:
            self.close_position(position)

    def calculate_williams_fractals(high_prices, low_prices):
        fractal_highs = []
        fractal_lows = []

        for i in range(2, len(high_prices) - 2):
            if high_prices[i] > high_prices[i - 1] and high_prices[i] > high_prices[i - 2] and \
                    high_prices[i] > high_prices[i + 1] and high_prices[i] > high_prices[i + 2]:
                fractal_highs.append((i, high_prices[i]))

            if low_prices[i] < low_prices[i - 1] and low_prices[i] < low_prices[i - 2] and \
                    low_prices[i] < low_prices[i + 1] and low_prices[i] < low_prices[i + 2]:
                fractal_lows.append((i, low_prices[i]))

        return fractal_highs, fractal_lows


    def cal_curr_price_deviation(self,symbol):
        positions = mt5.positions_get(symbol=symbol)
        position = positions[len(positions) - 1]
        initial_price = position.price_open
        current_price = mt5.symbol_info_tick(symbol).ask
        deviation = ((current_price - initial_price) / initial_price) * 100 * 100
        if self.direction == "buy":
            return deviation
        if self.direction == "sell":
            return deviation * -1
    
    def adjust_stop_loss(self):
        # Implementa la lógica para ajustar el stop loss aquí
        # Por ejemplo, podrías modificar el stop loss de todas las posiciones abiertas
        # o ajustar el stop loss solo de las últimas operaciones, dependiendo de tu estrategia
        if self.win_count == 10:
            # Ajustar el stop loss aquí según tu estrategia
            nuevo_stop_loss = self.stop_loss - 10  # Ejemplo: Reducir el stop loss en 10 pips
            print(f"¡Se han alcanzado 10 operaciones ganadoras! Ajustando el stop loss a {nuevo_stop_loss}")
            self.stop_loss = nuevo_stop_loss
            self.win_count = 0 
    
    def run(self):
        if not self.is_trading_day():
            return
        
        ny_timezone = pytz.timezone('America/New_York')

        while True:
             # Obtiene la hora actual en la zona horaria de Nueva York
            current_time = datetime.datetime.now(ny_timezone).time()

            if datetime.time(7, 0) <= current_time <= datetime.time(13, 0):
                for timeframe in self.timeframes:
                    historical_data = get_historical_data(symbol=self.symbol, timeframe=timeframe)

                
                self.market_order(self.symbol, self.volume, self.direction)
                pos = mt5.positions_get(symbol=self.symbol)
                if len(pos) > 0:
                    self.daily_entries.append({
                        "Symbol": self.symbol,
                        "Time": datetime.now(),
                        # Agregar otros datos relevantes de la entrada diaria
                    })
                    for p in pos:
                        self.transactions.append({
                            "Symbol": p.symbol,
                            "Type": "Buy" if p.type == mt5.ORDER_TYPE_BUY else "Sell",
                            "Volume": p.volume,
                            "Open Price": p.price_open,
                            "Close Price": p.price_current,
                            "Profit": p.profit,
                            "Time": datetime.now(),
                            # Agregar otros datos relevantes de la transacción
                    })
                    curr_no_of_safty_orders = 0
                    multiplied_volume = self.volume * 2
                    deviation = -1
                    next_price_level = -1

                    is_ok = True
                    while is_ok:
                        curr_price_deviation = self.cal_curr_price_deviation(self.symbol)
                        if curr_price_deviation <= next_price_level:
                            if curr_no_of_safty_orders < self.no_of_safty_orders:
                                self.market_order(self.symbol, multiplied_volume, self.direction)
                                multiplied_volume *= 2
                                deviation *= 2
                                next_price_level += deviation
                                curr_no_of_safty_orders += 1
                        self.check_profit_loss(self.symbol)
                        try:
                            pct_profit = self.cal_pct_profit(self.symbol)
                        except:
                            pass
                        if pct_profit >= self.profit_target:
                            self.close_all(self.symbol)
                            is_ok = False
                        self.adjust_stop_loss()
            else:
                time.sleep(60)