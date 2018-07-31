"""
Dogs Dataset
    Class wrapper for interfacing with the dataset of dog images
    Usage:
        - from data.dogs import DogsDataset
        - python -m data.dogs
"""
import numpy as np
import os
from utils import get, impute_list
import re
import random
import pickle

class RoadDataset:
    def __init__(self, filename):
        # Load in all the data we need from disk
        self.max_time = get('X_dim')[1] + 10
        self.test_split = get('test_split')
        self.filename = get('data_folder') + filename

    def load_data(self):
        """
        Loads a single data partition from file.
        """
        f = open(self.filename, 'r')
        Xs, Ys = pickle.load(f)
        f.close()
        assert len(Xs) == len(Ys)
        split = len(Xs) - int(len(Xs) * self.test_split)
        assert split > 0
        assert split < len(Xs)

        x_train = [[[[x] for x in impute_list(y,self.max_time)] for y in z] for z in Xs[0:split]]
        y_train = [impute_list(y,self.max_time) for y in Ys[0:split]]
        x_test = [[[[x] for x in impute_list(y,self.max_time)] for y in z] for z in Xs[split:]]
        y_test = [impute_list(y,self.max_time) for y in Ys[split:]]

        # x_train = [[[[x] for x in y] for y in z] for z in Xs[0:split]]
        # y_train = Ys[0:split]
        # x_test = [[[[x] for x in y] for y in z] for z in Xs[split:]]
        # y_test = Ys[split:]
        
        # x_train = Xs[0:split]
        # y_train = Ys[0:split]
        # x_test = Xs[split:]
        # y_test = Ys[split:]

        return np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test) 

if __name__ == '__main__':
    road = RoadDataset()
    print("Train:\t", len(road.trainX))
    print("Test:\t", len(road.testX))
