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
np.set_printoptions(edgeitems=30)

def train():
    # read filenames
    try:
        os.mkdir(WEIGHTS_FOLDER)
    except:
        print "weight folder exist"
    filenames = [x for _, _, x in os.walk(DATA_FOLDER)]
    for filename in filenames[0]:
        # define input data:
        train_road(filename)


def train_road(filename):
    road = RoadDataset(filename)
    x_train, y_train, x_test, y_test = road.load_data()
    print len(x_train[0]), len(x_train[0][0])
    print x_train[1]
    print y_train[1]
    exit(0)

    # get cnn model
    model = generate_model()
    plot_model(model, to_file='model.png')

    print("training ...")
    callbacks = [ModelCheckpoint(WEIGHTS_FOLDER + "weights_" + filename, 
                                 monitor='val_loss', save_best_only=True)]
    history = model.fit(x_train, y_train,
              batch_size=BATCH_SIZE,
              epochs=CNN_EPOCHS,
              verbose=1,
              validation_split=VALIDATION_SPLIT,
              callbacks=callbacks)

    max_val_loss, idx = min((val, idx) for (idx, val) in enumerate(history.history['val_loss']))
    print('Min validation loss = {0:.4f} (epoch {1:d})'.format(max_val_loss, idx+1))

    print("loading cnn weight ...")
    model.load_weights(WEIGHTS_FOLDER + "weights_" + filename)

    print("testing cnn performance ...")
    score = model.evaluate(x_test, y_test, batch_size=BATCH_SIZE, verbose=0)
    print('Test loss:', score[0], 'Test accuracy:', score[1])

    #print("CNN predicting ...")
    #features_test = model.predict(x_test, batch_size=BATCH_SIZE)

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