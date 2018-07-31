import numpy as np
from keras.callbacks import ModelCheckpoint
from keras import backend as K
from keras.utils import plot_model
from road import RoadDataset
import os
import pickle
import sys
from utils import get
from road import RoadDataset
from cnn import *
import shutil

# Initialize global variables
WEIGHTS_FOLDER = get('cnn.weights_folder')
VALIDATION_SPLIT = get('cnn.validation_split')
BATCH_SIZE = get('cnn.batch_size')
CNN_EPOCHS = get('cnn.cnn_epochs')
DATA_FOLDER = get('data_folder')
np.set_printoptions(edgeitems=6)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def train():
    # read filenames
    try:
        os.mkdir(WEIGHTS_FOLDER)
    except:
        print "weight folder exist"
    filenames = [x for _, _, x in os.walk(DATA_FOLDER)]
    for filename in filenames[0]:
        # define input data:
        if filename.split(".")[-1] == 'p':
            print "\n" + filename
            train_road(filename)


def train_road(filename):
    road = RoadDataset(filename)
    x_train, y_train, x_test, y_test, row_id_train, row_id_test, timestamp_train, timestamp_test = road.load_data()
    # print x_train[1]
    # print y_train[1]
    # print timestamp_train[1]
    # exit(0)

    # get cnn model
    model = generate_model()
    plot_model(model, to_file='model.png')

    callbacks = [ModelCheckpoint(WEIGHTS_FOLDER + "weights_" + filename, 
                                 monitor='val_loss', save_best_only=True)]
    history = model.fit([x_train, timestamp_train], y_train,
              batch_size=BATCH_SIZE,
              epochs=CNN_EPOCHS,
              verbose=0,
              validation_split=VALIDATION_SPLIT,
              callbacks=callbacks)

    max_val_loss, idx = min((val, idx) for (idx, val) in enumerate(history.history['val_loss']))
    print('Min validation loss = {0:.4f} (epoch {1:d})'.format(max_val_loss, idx+1))

    model.load_weights(WEIGHTS_FOLDER + "weights_" + filename)

    score = model.evaluate([x_test, timestamp_test], y_test, batch_size=BATCH_SIZE, verbose=0)
    print 'Test loss:', score[0], 'Test mae:', score[1]

    predict_result = model.predict([x_test, timestamp_test], batch_size=BATCH_SIZE)
    print bcolors.WARNING + "Test error %: ", score[1] / np.mean(y_test), bcolors.ENDC
    if  score[1] / np.mean(y_test) > 0.5:
        print "BAO ZHA LA !!!!!!!!!!!!!!!!!!!!!!!!!!"

def clean():
    try:
        shutil.rmtree(WEIGHTS_FOLDER)
    except:
        print "error cleaning"

if __name__ == "__main__":
    argv = sys.argv + [None] * 2
    if argv[1] == 'clean':
        clean()
    train()