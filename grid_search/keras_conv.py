import hashlib
import json
import sys
import ta
from keras.wrappers.scikit_learn import KerasClassifier, KerasRegressor
from scipy.signal import argrelextrema
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from utils.portfolio_predict_utils import make_max_sharpe_dataset, make_training_testing_datasets, plot, \
    make_sector_dataset

sys.path.append("..")
from utils.db.Db import Db
from auto_trading import AutoTrader
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from keras.layers import Dense, Dropout, Conv2D, Flatten, MaxPooling2D, BatchNormalization, Activation
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras import backend as K
import keras
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder

if __name__ == "__main__":
    """
    Attempt to use negative correlation to predict buy and sell signals
    1. Collect efficient frontier maximum sharpe ratio portfolio for a category 
    2. Collect all technical analysis features for symbols used in efficient portfolio
    3. Compute historical maxes and mins for highest percentage symbol in efficient portfolio 
        to generate optimal buy and sell signals
    4. Construct a time series dataset with all features from all symbols in efficient portfolio 
        including buy and sell signals for target symbol.
    5. Train Keras Conv net to predict by and sell signals
    """
    sd = make_sector_dataset()
    # data is now fully collected for all assets in the portfolio including
    ttd = make_training_testing_datasets(sd.df)
    x_train, x_test, input_shape = ttd.as_conv()

    def create_model(
            optimizer='adam'
    ):
        model = Sequential()
        model.add(Conv2D(128, kernel_size=(5, 5), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D())
        model.add(Conv2D(128, (5, 5)))
        model.add(BatchNormalization())
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (5, 5)))
        model.add(BatchNormalization())
        model.add(Activation("relu"))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D())
        model.add(Flatten())
        model.add(Dense(700, activation='relu'))
        model.add(Dense(1, activation='softmax'))
        print(model.summary())
        model.compile(
            loss='mean_squared_error',
            optimizer=optimizer,
            metrics=['accuracy']
        )
        return model


    model = KerasRegressor(
        build_fn=create_model,
        verbose=True,
        class_weight="balanced"
    )
    clf = GridSearchCV(
        model,
        {
            "optimizer": ['SGD'],
            # "hidden_layer_size": [700],
        },
        n_jobs=1,
        verbose=True
    )
    grid_result = clf.fit(x_train, ttd.y_train)
    # Best paramete set
    print('Best parameters found:\n', clf.best_params_)

    # All results
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, grid_result.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

    test_output = clf.predict(x_test)
    test_output = test_output.ravel()
    test_dates = sd.dates[-len(ttd.testing_data):].tolist()

    print(metrics.regression.mean_absolute_error(ttd.y_test, test_output))
    print(metrics.regression.mean_absolute_error(ttd.y_test, test_output))
    # print(metrics.classification_report(ttd.y_test, test_output))
    # print(metrics.confusion_matrix(ttd.y_test, test_output))

    plot(sd, test_dates, test_output)
