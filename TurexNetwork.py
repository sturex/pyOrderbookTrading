import os
from keras import models
from keras import layers
from keras.utils import to_categorical
from keras import initializers
from keras import optimizers
import numpy
import json


class TurexNetwork:

    def __init__(self):
        self.model = None

    def create_model(self, network_structure):
        if len(network_structure) <= 2:
            raise Exception('The network must contain at least two layers')

        self.input_size = network_structure[0]
        self.output_size = network_structure[-1]
        
        self.model = models.Sequential()    
        self.model.add(layers.Dense(self.input_size, activation = 'sigmoid'))  
        for neurons_count in network_structure[1: -1]:        
            self.model.add(layers.Dense(neurons_count, activation = 'sigmoid'))        
        self.model.add(layers.Dense(self.output_size, activation = 'softmax'))
        self.model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
        
    def load_model(self, path_to_file):
        self.model = models.load_model(path_to_file)        
        
        layers = self.model.layers
        
        if len(layers) <= 2:
            raise Exception('The network must contain at least two layers')

        self.input_size = len(layers[0].get_weights()[1])
        self.output_size = len(layers[-1].get_weights()[1])
    
    def save_model(self, path_to_file):
        models.save_model(self.model, path_to_file)

    def train(self, train_folder):

        if self.model == None:
            return

        input_files = [f for f in os.listdir(train_folder) if os.path.isfile(os.path.join(train_folder, f))]     
        
        for in_file in input_files:
            with open(os.path.join(train_folder, in_file), 'r') as f:
                input_data = []
                output_data = []
                for line in f.readlines():
                    json_line = json.loads(line)

                    input_data.append(json_line['volumes'])
                    output_data.append(json_line['direction'])

                input_dataset = numpy.asarray(input_data)
                output_dataset = to_categorical(numpy.asarray(output_data))
                self.model.fit(input_dataset, output_dataset)


    def predict(self, _volumes):
        if len(_volumes) != self.input_size:
            return None
        input_dataset = numpy.asarray([_volumes])
        return self.model.predict(input_dataset)[0]

