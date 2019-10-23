import os
import json
from contextlib import suppress
from OrderBook import *
from Signal import Signal


class OrderBookContainer:
    def __init__(self, path_to_file):

        self.order_books = []
        self.trades = []
        self.cur_directory = os.path.dirname(path_to_file)
        self.f_name = os.path.split(path_to_file)[1]

        with open(path_to_file, 'r') as infile:
            for line in infile:
                ob = json.loads(line)
                self.order_books.append(OrderBook(ob))
    
    def create_training_dataset(self):
        if not self.order_books:
            return
        
        output_dir = os.path.join(self.cur_directory, 'Datasets')

        with suppress(OSError):
            os.mkdir(output_dir)

        dataset_file_path = os.path.splitext(os.path.join(output_dir, self.f_name))[0] + '.ds'

        best_prices = self.order_books[0].best_prices
        mid_price = (best_prices['buy_price'] + best_prices['sell_price']) / 2

        with open(dataset_file_path, 'w') as json_file:
            for idx, ob in enumerate(self.order_books[0:-1]):
                                
                next_best_prices = self.order_books[idx + 1].best_prices
                next_mid_price = (next_best_prices['buy_price'] + next_best_prices['sell_price']) / 2

                if mid_price != next_mid_price:
                    direction = 0 if mid_price > next_mid_price else 1                    
                    json.dump({'volumes': ob.volumes, 'direction': direction}, json_file)
                    json_file.write('\n')
                
                mid_price = next_mid_price


    def _open_position(self, best_prices, signal):
        self.trades.append({})

        self.trades[-1]['direction'] = signal                
        self.trades[-1]['open_time'] = best_prices['time']; 

        if signal == Signal.BUY:
            self.trades[-1]['open_price'] = best_prices['buy_price'];
        elif signal == Signal.SELL:
            self.trades[-1]['open_price'] = best_prices['sell_price'];
        
    def _close_position(self, best_prices):              
        self.trades[-1]['close_time'] = best_prices['time']; 

        if self.trades[-1]['direction'] == Signal.BUY:
            self.trades[-1]['close_price'] = best_prices['sell_price'];
        elif self.trades[-1]['direction'] == Signal.SELL:
            self.trades[-1]['close_price'] = best_prices['buy_price'];
        
    def _reverse_position(self, best_prices, signal):
        self._close_position(best_prices)
        self._open_position(best_prices, signal)            

    def backtest(self, generator, threshold):
        self.trades = []   

        for ob in self.order_books[0:-1]:            
            best_prices = ob.best_prices
            signal = generator(ob.volumes, threshold)

            if not self.trades and signal != Signal.WAIT:
                self._open_position(best_prices, signal)
            elif signal != self.trades[-1]['direction'] and signal != Signal.WAIT:
                self._reverse_position(best_prices, signal)
        
        if not self.trades:
            best_prices = self.order_books[-1].best_prices
            self._close_position(best_prices)

        return self.trades


    def backtest_n(self, generator, ffnn, threshold):
        self.trades = []   

        for ob in self.order_books[0:-1]:            
            best_prices = ob.best_prices
            signal = generator(ffnn, ob.volumes, threshold)

            if not self.trades and signal != Signal.WAIT:
                self._open_position(best_prices, signal)
            elif signal != self.trades[-1]['direction'] and signal != Signal.WAIT:
                self._reverse_position(best_prices, signal)
        
        if not self.trades:
            best_prices = self.order_books[-1].best_prices
            self._close_position(best_prices)

        return self.trades

