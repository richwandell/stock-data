import ta
from scipy.signal import argrelextrema
import numpy as np
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

from auto_trading import AutoTrader
import pandas as pd
from datetime import datetime
from datetime import timedelta


class MLPAutoTrader(AutoTrader):

    def get_trades(self, time_delta=timedelta(days=365))->pd.DataFrame:
        df = self.df.copy()
        df[self.date_time] = pd.to_datetime(df[self.date_time])
        scatter_data = df[[self.close, self.date_time]].as_matrix()
        dates = scatter_data[:, 1]

        mins = argrelextrema(df[self.close].as_matrix(), np.less, order=5)
        mins_dates = dates[mins[0]]
        maxes = argrelextrema(df[self.close].as_matrix(), np.greater, order=5)
        maxes_dates = dates[maxes[0]]

        df = df.set_index(self.date_time)
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

        scaler = preprocessing.StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)

        mlpc = MLPClassifier(
            verbose=False,
            hidden_layer_sizes=(200, 20),
            tol=1e-10,
            alpha=0.001,
            learning_rate='adaptive'
        )
        mlpc.fit(x_train_scaled, y_train)

        x_test_scaled = scaler.transform(x_test)
        test_output = mlpc.predict(x_test_scaled)

        test_dates = dates[-len(testing_data):].tolist()
        test_output = test_output.tolist()
        frame = np.column_stack((test_dates, test_output))
        signals = pd.DataFrame(frame, columns=[self.date_time, 'signal'])
        signals['signal'] = pd.to_numeric(signals['signal'])
        return signals.set_index(self.date_time)
