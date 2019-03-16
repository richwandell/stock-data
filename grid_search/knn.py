import sys

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

sys.path.append("..")
from utils.portfolio_predict_utils import make_max_sharpe_dataset, make_training_testing_datasets, plot, \
    make_sector_dataset
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
import numpy as np

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
    sd = make_sector_dataset('AAPL')
    # data is now fully collected for all assets in the portfolio including
    ttd = make_training_testing_datasets(sd.df)
    model = KNeighborsClassifier(weights='distance')
    clf = GridSearchCV(
        model,
        {
            "algorithm": [
                "auto",
                "ball_tree",
                "kd_tree",
                "brute"
            ]
        },
        scoring='f1_micro',
        n_jobs=14,
        verbose=True
    )
    clf.fit(ttd.x_train_scaled, ttd.y_train)
    # Best paramete set
    print('Best parameters found:\n', clf.best_params_)

    # All results
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

    test_output = clf.predict(ttd.x_test_scaled).tolist()
    test_dates = sd.dates[-len(ttd.testing_data):].tolist()

    print(metrics.classification_report(ttd.y_test, test_output))
    print(metrics.confusion_matrix(ttd.y_test, test_output))

    plot(sd, test_dates, test_output)

