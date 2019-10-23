import websocket
import threading
import traceback
import datetime
from time import sleep
import json
import urllib
import math
from my_utils import *
from OrderBook import OrderBook

#included in bitmex_websocket package
from util.api_key import generate_nonce, generate_signature


#the sources with changes taken from https://github.com/BitMEX/api-connectors/tree/master/official-ws/python
class BitmexOrderBookSaver:

    def __init__(self, api_key, api_secret, folder):
                
        self.out_file = None 
        self.cur_YYYYMMDD = 0
        self.folder = folder

        self.L2 = {}
        self.L2['Buy'] = {}
        self.L2['Sell'] = {}
        
        self.api_key = api_key
        self.api_secret = api_secret

        self.data = {}
        self.keys = {}

        self.is_connected = self._connect('wss://www.bitmex.com/realtime?subscribe=orderBookL2:XBTUSD')
        
        if self.is_connected == False:            
            return None

        self._wait_for_account()  

    def exit(self):
        self.ws.close()
        sleep(0.1)

    def _connect(self, wsURL):
        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self._on_message,
                                         on_close=self._on_close,
                                         on_open=self._on_open,
                                         on_error=self._on_error,
                                         header=self._get_auth())

        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()

        conn_timeout = 10
        while not self.ws.sock or not self.ws.sock.connected and conn_timeout:
            sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            self.exit()
            raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')
        
        return True

    def _get_auth(self):
        nonce = generate_nonce()
        return [
            f"api-nonce: {nonce}",
            f"api-signature: {generate_signature(self.api_secret, 'GET', '/realtime', nonce, '')}",
            f"api-key:{self.api_key}"
        ]

    def _wait_for_account(self):
        while not {'orderBookL2'} <= set(self.data):
            sleep(0.1)

    def _send_command(self, command, args=None):
        if args is None:
            args = []
        self.ws.send(json.dumps({"op": command, "args": args}))            

    def get_orderbook(self):
        orderbook = {}
        
        cur_UTC = datetime.datetime.utcnow()

        orderbook['date'] = get_YYYYMMDD(cur_UTC)
        orderbook['time'] = get_HHMMSSmmm(cur_UTC)

        orderbook['prices'] = [] 
        orderbook['volumes'] = []      

        #only even values are applicable
        half_size = 50

        sell_side = sorted(self.L2['Sell'].items())
        buy_side = sorted(self.L2['Buy'].items(), reverse=True)

        buy_side_len = len(buy_side)
        sell_side_len = len(sell_side)

        if buy_side_len < half_size or sell_side_len < half_size:
            return None
        
        for idx in reversed(range(0, half_size)):
            orderbook['prices'].append(buy_side[idx][0])
            orderbook['volumes'].append(buy_side[idx][1])

        for idx in range(0, half_size):
            orderbook['prices'].append(sell_side[idx][0])
            orderbook['volumes'].append(sell_side[idx][1])

        return OrderBook(orderbook)

    def _save_orderbook(self):
        
        orderbook = self.get_orderbook()

        if orderbook is not None: 
            if self.out_file == None or self.cur_YYYYMMDD != orderbook.date:
                self.cur_YYYYMMDD = orderbook.date
                f_path = self.folder + '\\' + 'XBTUSD_' + str(self.cur_YYYYMMDD) + '.txt'
                self.out_file = open(f_path, 'a+')
             
            orderbook.write(self.out_file)

    def _on_message(self, ws, message):
        message = json.loads(message)
        table, action = message.get('table'), message.get('action')
        
        try:            
            if action:
                if table not in self.data:
                    self.data[table] = []

                if table == 'orderBookL2':

                    if action in ('partial', 'insert'):
                        for item in message['data']:
                            self.L2[item["side"]][item['price']] = item['size']                            

                    elif action == 'update':      
                        for item in message['data']:
                            pr = get_price_from_ID(item['id'])

                            self.L2[item["side"]][pr] = item['size']

                    elif action == 'delete':  
                        for item in message['data']:
                            pr = get_price_from_ID(item['id'])
                            del self.L2[item["side"]][pr]

                    self._save_orderbook();
        except:
            print(traceback.format_exc())


    def _on_error(self, ws, error):
        self.ws.close()

    def _on_open(self, ws):
        pass

    def _on_close(self, ws):
        pass



