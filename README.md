## With this sample framework you`ll be able to:
* get order book (Level II, market depth) from [BitMEX](https://www.bitmex.com) and save as json structures in day-lenght files
* generate trading signals [BUY, SELL, WAIT] on orderbooks (not only BitMEX\`s) with or without help of sequential neural network
* create training dataset for neural network from presaved orderbooks
* create, train, save and restore neural network with input data of orderbooks (not only BitMEX`s)
* perform backtest trading with output of trades

## Additional external info
The closely related ideas are also exposed in "One Way to Trading over Orderbook Analisys" [article on Medium](https://medium.com/@sturex/one-way-to-trading-over-orderbook-analisys-689475ae839f).
Read the article for better understanding.

### Limitations
* [BitMEX](https://www.bitmex.com) only and [XBTUSD](https://www.bitmex.com/app/contract/XBTUSD) data fetching only are provided. The source connection code taken from [Python Adapter for BitMEX Realtime Data](https://github.com/BitMEX/api-connectors/tree/master/official-ws/python)
* Code works correctly only for 100-depth order books.
* Neural network has voluntaristic rigid architecture where you can operate only number of layers and neurons quantity. Input layer must contain 100 neurons, output layer 2 neurons.
* No commissions, fees etc. are calculated while backtesting. Result trades must be extra analyzed.


## Installation
```
pip install -r requirements.txt
```

## Use cases
#### Retrieving order books ([Bitmex](https://www.bitmex.com) only)
Just run code below with your [API-key credentials to BitMEX](https://www.bitmex.com/app/apiKeysUsage).
On every update of market 100-depth order book is writing to disk.
[Bid-ask spread](https://en.wikipedia.org/wiki/Bid-ask_spread) is in the middle of order book. New trading day starts with new file.

```python
from BitmexOrderBookSaver import *
api_key = ''
api_secret = ''
save_folder = ''
bitmex = BitmexOrderBookSaver(api_key, api_secret, save_folder)
print('Retrieving orderbooks market data. Press any key to stop')
input()
bitmex.exit()
```

	
#### Dataset creation for neural network training

```python
from OrderBookContainer import *

folder=''
input_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]     
for in_file in input_files:
	obc = OrderBookContainer(os.path.join(folder, in_file))
	obc.create_training_dataset()
```
As a result the script will create Datasets subfolder with \*.ds files. 


#### Neural network creation, training and saving for next time use

My goal is just to show that neural networks work without price movement analysis but only on current market timestamp (== order book) analysis. 

So, network gets only order book volumes as input and generates floating point value as output. **Really, there are no prices in input data!**

- Is it possible to predict price movements without price analysis?
- Yes!

The code below will create three-layered feed-forward sequential network. I use [Keras framework](https://keras.io/).

I use sigmoid activation function for all layers except for last one where softmax is used.
The first layer consists of 100 neurons, one for each line in order book.
The last layer must contain of 2 neurons because of two variants are possible - BUY and SELL.

```python
import TurexNetwork 
	
nwk = TurexNetwork.TurexNetwork()
nwk.create_model((100, 50, 2)) 
datasets_folder=''
nwk.train(datasets_folder)
nwk.save_model('full_path_to_file.h5')
```

#### Trading signal generation

You can generate trading signal with possible values of [BUY, SELL, WAIT] with order book analysis only. 
On every *orderbook*  you get from exchange or read from file signal can be generated with code below.
*threshold* is floating point value in range [0, 1]. The less the value the more signals you get. 
###### Neural generator

```python
from Generators import sample_generator_n
nwk = TurexNetwork.TurexNetwork()
nwk.load_model('model_from_code_above.h5')
signal = sample_generator_n(nwk, orderbook.volumes, threshold)
```
###### Simple generator
```python
from Generators import sample_generator
signal = sample_generator(orderbook.volumes, threshold)
```


#### Backtesting
The mean of *threshold*  is described above.

```python
import TurexNetwork
import Generators 
from OrderBookContainer import *

obc = OrderBookContainer('path_to_file')

nwk = TurexNetwork.TurexNetwork()
nwk.load_model('path_to_file.h5')
threshold = 0.0
trades = obc.backtest_n(Generators.sample_neural_generator, nwk, threshold)
#trades = obc.backtest(Generators.sample_generator, threshold)
for trade in trades:
    print(trade)
```
