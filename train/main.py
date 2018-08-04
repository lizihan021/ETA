import numpy as np
from keras.callbacks import ModelCheckpoint
from keras import backend as K
from keras.utils import plot_model
from road import RoadDataset
import os
import pickle
import sys
from utils import get, mov_avg
from road import RoadDataset
from cnn import *
import shutil
import matplotlib.pyplot as plt
import psycopg2

# Initialize global variables
WEIGHTS_FOLDER = get('cnn.weights_folder')
VALIDATION_SPLIT = get('cnn.validation_split')
BATCH_SIZE = get('cnn.batch_size')
CNN_EPOCHS = get('cnn.cnn_epochs')
DATA_FOLDER = get('data_folder')
PLOT_FOLDER = get('plot_folder')
uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
np.set_printoptions(edgeitems=30)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def train(folder_name, train_flag = True):
    # read filenames
    try:
        os.mkdir(WEIGHTS_FOLDER)
        os.mkdir(PLOT_FOLDER)
    except:
        print "weight folder exist"
    filenames = [x for _, _, x in os.walk(folder_name)]
    for i, filename in enumerate(filenames[0]):
        # define input data:
        if filename.split(".")[-1] == 'p' and not os.path.isfile(WEIGHTS_FOLDER + "weights_" + filename):
            print "\n" + str(i) + ': ' + filename
            try:
                train_road(filename, folder_name, train_flag)
            except ValueError:
                print bcolors.WARNING + "Too few sample" + bcolors.ENDC
                continue
        else:
            print bcolors.WARNING + "Trained: " + filename + bcolors.ENDC


def train_road(filename, folder_name, train_flag = True):
    road = RoadDataset(folder_name, filename)
    x_train, y_train, x_test, y_test, row_id_train, row_id_test, \
    timestamp_train, timestamp_test, y_time = road.load_data()
    # print x_train[1]
    # print y_train[1]
    # print timestamp_train[1]
    # exit(0)

    # get cnn model
    model = generate_model()
    #plot_model(model, to_file='model.png')

    if train_flag:
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
    print 'ML model test mae:', score[1] #'Test loss:', score[0], 

    predict_result = model.predict([x_test, timestamp_test], batch_size=BATCH_SIZE)
    # print predict_result
    # print y_test
    plot_pred = [z[0] for z in predict_result]
    plot_y = [z[0] for z in y_test] # [260:468]
    mavg = mov_avg(plot_y, 4)
    err = 0;
    for i, tmp1 in enumerate(plot_y):
        err = err + abs(tmp1-mavg[i])
    print "Moving avg test mae: ", err / len(plot_y)
    # x_points = xrange(len(plot_y))
    # # x_points = [z/70.0 for z in x_points]
    # # fig = plt.figure()
    # # ax = fig.add_subplot(211)
    # fig = plt.figure()
    # fig.suptitle(str(score[1]) + '\n' + str(err / len(plot_y)) +'\n'+str(score[1] / np.mean(y_test)))
    # ax = plt.subplot(111)
    # ax.plot(x_points, plot_y, 'b', label="actual")
    # ax.plot(x_points, plot_pred, 'r', label="CNN predict")
    # ax.plot(x_points, mavg, 'g', label="moving avg")
    # ax.legend()
    # #fig.xlim([0,len(plot_y)+1])
    # plt.xlabel("Day")
    # plt.ylabel("Speed (m/s)")
    # #fig.show()
    # fig.savefig(PLOT_FOLDER + filename + '.png')

    print bcolors.WARNING + "Test error %: ", score[1] / np.mean(y_test), bcolors.ENDC
    if  score[1] / np.mean(y_test) > 0.4:
        print "BAO ZHA LA !!!!!!!!!!!!!!!!!!!!!!!!!!"
    else :
        create_table(y_time)
        insert_table(filename.split('.')[0], plot_pred, y_time)

def create_table(timestamp_test):
    for timestamp in timestamp_test:
        try:
            conn = psycopg2.connect(uri)
            stmt = '''CREATE TABLE time_{} (
                    osm_id bigint,
                    source_id bigint,
                    target_id bigint,
                    predict_speed double precision
                );\n'''.format(timestamp)
            cur = conn.cursor()
            cur.execute(stmt)
            conn.commit()
            conn.close()
        except:
            conn.close()

def insert_table(filename, predict_result, timestamp_test):
    assert len(predict_result) == len(timestamp_test)
    conn = psycopg2.connect(uri)
    osm_id, source_id, target_id = filename.split('_')
    for timestamp, speed in zip(timestamp_test, predict_result):
        stmt = '''INSERT into time_{} (osm_id, source_id, target_id, predict_speed) VALUES ({},{},{},{});\n'''.\
                    format(timestamp, osm_id, source_id, target_id, speed)
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()

def clean():
    try:
        shutil.rmtree(WEIGHTS_FOLDER)
        shutil.rmtree(PLOT_FOLDER)
    except:
        print "error cleaning"
    conn = psycopg2.connect(uri)
    stmt = ''' SELECT CONCAT('DELETE FROM ',t.table_name,';') AS stmt
               FROM information_schema.tables t
              WHERE t.table_schema = 'public'
                AND t.table_name LIKE 'time%'            
              ORDER BY t.table_name; '''
    cur = conn.cursor()
    cur.execute(stmt)
    for i, line in enumerate(cur):
        if i%100 == 9:
            print "processed {} time".format(i + 1)
        cur = conn.cursor()
        cur.execute(line[0])
        conn.commit()
    conn.close()

if __name__ == "__main__":
    argv = sys.argv + [None] * 2
    if argv[1] == 'clean':
        clean()
        train(argv[2], True)
    elif argv[1] == 'notrain':
        train(argv[2], False)
    else:
        train(argv[1], True)