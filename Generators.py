from Signal import Signal
from TurexNetwork import *

    
def sample_generator(volumes, threshold):
    
    height = len(volumes)

    h1 = sum(volumes[0:int(height / 2) + 1])
    h2 = sum(volumes[int(height / 2):height + 1])

    ind = (h2-h1) / (h2+h1)
                
    if ind > threshold:
        return Signal.SELL
    elif ind < -threshold:
        return Signal.BUY
    else:
        return Signal.WAIT

    
def sample_neural_generator(turex_network, volumes, threshold):
    
    prediction = turex_network.predict(volumes)
    
    ind = prediction[1] - prediction[0]

    if ind > threshold:
        return Signal.SELL
    elif ind < -threshold:
        return Signal.BUY
    else:
        return Signal.WAIT
