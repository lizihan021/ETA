"""
Dogs Dataset
    Class wrapper for interfacing with the dataset of dog images
    Usage:
        - from data.dogs import DogsDataset
        - python -m data.dogs
"""
import numpy as np
import os
from utils import get, impute_list, unix2week
import re
import random
import pickle

class RoadDataset:
    def __init__(self, folder_name, filename):
        # Load in all the data we need from disk
        self.max_time = get('X_dim')[1] + 10
        self.test_split = get('test_split')
        self.filename = folder_name + filename

    def load_data(self):
        """
        Loads a single data partition from file.
        """
        f = open(self.filename, 'r')
        row_id, Xs, Ys, timestamp = pickle.load(f)
        f.close()
        assert len(Xs) == len(Ys)
        if len(Xs) < 10:
            raise ValueError('too few train')
        split = len(Xs) - int(len(Xs) * self.test_split)
        assert split > 0
        assert split < len(Xs)

        x_train = [[[[x] for x in impute_list(y,self.max_time)] for y in z] for z in Xs[0:split]]
        y_train = [impute_list(y,self.max_time) for y in Ys[0:split]]
        x_test = [[[[x] for x in impute_list(y,self.max_time)] for y in z] for z in Xs[split:]]
        y_test = [impute_list(y,self.max_time) for y in Ys[split:]]

        timestamp_onehot = [unix2week(x) for x in timestamp]
        y_time = [x[2] for x in timestamp]

        return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test), \
               row_id[0:split], row_id[split:], np.array(timestamp_onehot[0:split]), \
               np.array(timestamp_onehot[split:]), np.array(y_time[split:])

if __name__ == '__main__':
    road = RoadDataset()
    print("Train:\t", len(road.trainX))
    print("Test:\t", len(road.testX))
