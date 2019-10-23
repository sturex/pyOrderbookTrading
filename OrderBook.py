import json

class OrderBook:
    def __init__(self, data):
        
        self._date = data['date']
        self._time = data['time']
        self._volumes = data['volumes']
        self._prices = data['prices']

        self._height = len(self._prices)
        
    @property
    def time(self):
        return self._time

    @property
    def date(self):
        return self._date

    @property
    def volumes(self):
        return self._volumes
    
    @property
    def best_prices(self):
        return { 'sell_price': self._prices[int(self._height / 2)], 'buy_price':  self._prices[int(self._height / 2) - 1], 'time': self._time}
    
    def write(self, json_file):
        json.dump({'date': self._date, 'time': self._time, 'prices': self._prices, 'volumes': self._volumes}, json_file)
        json_file.write('\n')

