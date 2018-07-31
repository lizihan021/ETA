import numpy as np
from keras.models import Sequential, Model
from keras.layers import Input, Conv2D, Dense, Dropout, MaxPooling2D, Flatten, Concatenate, concatenate
from keras import backend as K
from utils import get

INPUT_SIZE = get('X_dim')
OUTPUT_SIZE = get('Y_dim')
TIME_SIZE = get('time_dim')
DROPOUT_CNN = get('cnn.dropout_cnn')
DROPOUT_DENSE = get('cnn.dropout_dense')
OPTIMIZER = get('cnn.optimizer')

def generate_model():

	first_input = Input(shape=(INPUT_SIZE[0],INPUT_SIZE[1],1))
	conv1 = Conv2D(32, kernel_size=(5, 5),
	                 activation='relu',
	                 input_shape=(INPUT_SIZE[0],INPUT_SIZE[1],1) )(first_input)
	conv2 = Conv2D(64, (3, 3), activation='relu')(conv1)
	drop1 = Dropout(DROPOUT_CNN)(conv2)
	first_flat = Flatten()(drop1)

	second_input = Input(shape=(TIME_SIZE, ))
	second_dense = Dense(TIME_SIZE, )(second_input)

	merge_one = concatenate([first_flat, second_dense])

	dense1 = Dense(500, activation='relu')(merge_one)
	drop2 = Dropout(DROPOUT_DENSE)(dense1)
	final_out = Dense(OUTPUT_SIZE, activation='relu')(drop2)

	final = Model(inputs=[first_input, second_input], outputs=final_out)

	final.compile(loss='mean_squared_error',
	              optimizer=OPTIMIZER,
	              metrics=['mae'])

	return final