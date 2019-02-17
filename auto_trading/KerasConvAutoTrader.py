from scipy.signal import argrelextrema

from auto_trading import AutoTrader
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from keras.layers import Dense, Dropout, Conv2D, Flatten, MaxPooling2D
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras import backend as K
import keras
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder


class KerasConvAutoTrader(AutoTrader):

    def get_trades(self, time_delta=timedelta(days=365))->pd.DataFrame:
        df = self.df.copy()
        df[self.date_time] = pd.to_datetime(df[self.date_time])

        scatter_data = df[[self.close, self.date_time]].as_matrix()
        dates = scatter_data[:, 1]

        mins = argrelextrema(df['adjusted_close'].as_matrix(), np.less, order=5)
        mins_dates = dates[mins[0]]
        maxes = argrelextrema(df['adjusted_close'].as_matrix(), np.greater, order=5)
        maxes_dates = dates[maxes[0]]

        df = df.set_index('date_time')
        df['make_a_trade'] = 0
        df['make_a_trade'][mins_dates] = 1
        df['make_a_trade'][maxes_dates] = 2
        df = df.dropna()
        df = df.reset_index()
        training_data = df[df[self.date_time] < datetime.now() - time_delta]
        training_data = training_data[self.columns].as_matrix()
        x_train = training_data[:, 0:-1]
        y_train = training_data[:, -1].astype(int)

        testing_data = df[df[self.date_time] >= datetime.now() - time_delta]
        testing_data = testing_data[self.columns].as_matrix()
        x_test = testing_data[:, 0:-1]
        y_test = testing_data[:, -1].astype(int)

        chunk_height = 12
        original_size = x_train.shape[0]
        while original_size % chunk_height > 0:
            original_size -= 1
        x_train = x_train[-original_size:]
        y_train = y_train[-original_size:]
        chunk_size = int(original_size / chunk_height)

        Y = y_train.reshape(int(chunk_size), chunk_height)

        all_categories = np.apply_along_axis(np.array_str, 1, Y).tolist()
        unique_categories = list(np.unique(np.apply_along_axis(np.array_str, 1, Y).tolist()))

        for i, cat in enumerate(all_categories):
            all_categories[i] = unique_categories.index(cat)

        onehot_encoder = OneHotEncoder(sparse=False)
        onehot_encoded = onehot_encoder.fit_transform(all_categories)

        onehot = keras.utils.to_categorical(all_categories)

        if K.image_data_format() == 'channels_first':
            X = x_train.reshape(int(chunk_size), 1, chunk_height, 56)
            input_shape = (1, chunk_height, 56)
        else:
            X = x_train.reshape(int(chunk_size), chunk_height, 56, 1)
            input_shape = (chunk_height, 56, 1)

        model = Sequential()
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(Flatten())
        model.add(Dense(len(unique_categories), activation='softmax'))
        print(model.summary())
        model.compile(loss="categorical_crossentropy", optimizer=RMSprop(), metrics=['accuracy'])
        model.fit(X, onehot, epochs=400, verbose=1)

        print("done")



