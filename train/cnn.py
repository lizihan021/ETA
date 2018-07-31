import numpy as np
from keras.models import Sequential
from keras.layers import Input, Conv2D, Dense, Dropout, MaxPooling2D, Flatten
from keras import backend as K
from utils import get

INPUT_SIZE = get('X_dim')
OUTPUT_SIZE = get('Y_dim')
DROPOUT_CNN = get('cnn.dropout_cnn')
DROPOUT_DENSE = get('cnn.dropout_dense')
OPTIMIZER = get('cnn.optimizer')

def generate_model():
	# define CNN
	model = Sequential()
	# (9,9,1)
	model.add(Conv2D(32, kernel_size=(5, 5),
	                 activation='relu',
	                 input_shape=(INPUT_SIZE[0],INPUT_SIZE[1],1) ))
	# (5,5,32)
	model.add(Conv2D(64, (3, 3), activation='relu'))
	# (3,3,64)
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(DROPOUT_CNN))
	# (5,2,64)
	model.add(Flatten())
	# 640
	model.add(Dense(500, activation='relu'))
	# 500
	model.add(Dropout(DROPOUT_DENSE))
	# 500
	model.add(Dense(OUTPUT_SIZE, activation='relu'))

	model.compile(loss='mean_squared_error',
	              optimizer=OPTIMIZER,
	              metrics=['mae'])

	return model