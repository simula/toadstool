import os
import csv
import glob
import shutil
import time
import cv2

import numpy as np

from tensorflow.keras.utils import Sequence

import tensorflow.keras.backend as K

def load_image_tuple(path_tuple, delimiter=" "):

    frame_1 = cv2.imread(path_tuple[0][0])
    frame_2 = cv2.imread(path_tuple[0][1])
    frame_3 = cv2.imread(path_tuple[1])

    frame_1 = cv2.resize(frame_1, (224, 224))
    frame_2 = cv2.resize(frame_2, (224, 224))
    frame_3 = cv2.resize(frame_3, (224, 224))
    
    frame_1 = cv2.cvtColor(frame_1, cv2.COLOR_BGR2GRAY)
    frame_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2GRAY)
    frame_3 = cv2.cvtColor(frame_3, cv2.COLOR_BGR2GRAY)
    
    frame_1 = np.expand_dims(frame_1, axis=2)
    frame_2 = np.expand_dims(frame_2, axis=2)
    frame_3 = np.expand_dims(frame_3, axis=2)

    combined = np.concatenate((frame_1, frame_2, frame_3), axis=2)

    return np.array(combined, dtype=np.float32)

def read_sensor_data(path):
    data = []
    with open(path) as f:
        for line in f.read().splitlines():
            data.append(float(line))
    return np.array(data, dtype=np.float32)
    
def split_data_into_equal_parts(data, number_of_parts):
    part_length = len(data) // number_of_parts
    parts = []
    for index in range(number_of_parts - 1):
        parts += [ data[ index * part_length : (index + 1) * part_length ] ]
    parts += [ data[ (number_of_parts - 1) * part_length : len(data) ] ]
    return np.array(parts)

def load_data(x_paths, y_paths, n_folds=3, batch_size=32):

    x_splits = [[] for _ in range(n_folds)]
    y_splits = [[] for _ in range(n_folds)]
    
    for x_path, y_path in zip(x_paths, y_paths):

        image_data = list(glob.glob(os.path.join(x_path, "*")))

        game_data = list(filter(lambda x: os.path.basename(x).split("_")[0] == "game", image_data))
        face_data = list(filter(lambda x: os.path.basename(x).split("_")[0] == "face", image_data))

        game_data = list(sorted(game_data, key=lambda x: int(os.path.splitext(os.path.basename(x).split("_")[1])[0])))
        it = iter(game_data)

        game_data = list(zip(it, it))
        face_data = list(sorted(face_data, key=lambda x: int(os.path.splitext(os.path.basename(x).split("_")[1])[0])))

        x_data = [ frame_tuple for frame_tuple in zip(game_data, face_data) ]
        y_data = []
        y_data_raw = read_sensor_data(y_path)

        for index in range(len(x_data)):
            y_data.append(y_data_raw[index])

        split_x = split_data_into_equal_parts(x_data, n_folds)
        split_y = split_data_into_equal_parts(y_data, n_folds)

        for i in range(n_folds):
            x_splits[i].extend(split_x[i])
            y_splits[i].extend(split_y[i])

    x_splits = np.array(x_splits) 
    y_splits = np.array(y_splits) 

    for fold_index in range(n_folds):

        training_loader = DataGenerator(
            batch_size=batch_size,
            x_data=np.concatenate(x_splits[ np.arange(n_folds) != fold_index ]),
            y_data=np.concatenate(y_splits[ np.arange(n_folds) != fold_index ]),  
        )

        validation_loader = DataGenerator(
            batch_size=batch_size,
            x_data=x_splits[ fold_index ],
            y_data=y_splits[ fold_index ],
        )

        yield training_loader, validation_loader

class DataGenerator(Sequence):

    def __init__(self,
                 x_data: np.ndarray,
                 y_data: np.ndarray,
                 batch_size:int=1,
                 shuffle:bool=True,
                 *argv,
                 **kwargs):
        
        if not isinstance(x_data, np.ndarray):
            x_data = np.array(x_data)

        if not isinstance(y_data, np.ndarray):
            y_data = np.array(y_data)

        if len(x_data) == 0 or len(y_data) == 0:
            raise Exception("The length of X data or the length Y data is zero!")

        if len(x_data) != len(y_data):
            raise Exception("The length of X data does not equal the length Y data!")

        self.x_data = x_data
        self.y_data = y_data

        if len(self.x_data) % batch_size != 0:
            print("Batch size results in a rest of %s!" % str(len(self.x_data) % batch_size))

        self.batch_size = batch_size
        self.n_batches = len(self.x_data) // batch_size
        self.n_samples = self.n_batches * batch_size
        
        self.shuffle_permutation = np.random.permutation(len(self.x_data))

        print("%s samples split between %s batches" % (str(self.n_samples), str(self.n_batches)))

    def _get_index(self, index):
        return self.shuffle_permutation[
            index * self.batch_size :
            (index * self.batch_size) + self.batch_size
        ]

    def _load_x_batch(self, batch):
        return np.array([
            load_image_tuple(path, delimiter=" ") for path in batch
        ])

    def __len__(self):
        return int(np.floor(self.n_samples / self.batch_size))

    def __getitem__(self, index:int):

        current_batch_selection = self._get_index(index)
        
        x_batch = self._load_x_batch(
            np.array(self.x_data[ current_batch_selection ])
        )
        
        y_batch = np.array(self.y_data[ current_batch_selection ])

        return (x_batch, y_batch)
        
    def __iter__(self):
        """Create a generator that iterate over the Sequence."""
        for item in (self[i] for i in range(len(self))):
            yield item