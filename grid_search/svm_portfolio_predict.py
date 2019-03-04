import sys

from sklearn.svm import SVC

sys.path.append("..")
from sklearn.neural_network import MLPClassifier
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
    sd = make_sector_dataset()
    # data is now fully collected for all assets in the portfolio including
    ttd = make_training_testing_datasets(sd.df)

    # model = MLPClassifier(
    #     max_iter=50,
    #     tol=1e-20,
    #     solver='lbfgs',
    #     activation='relu'
    # )

    # clf = GridSearchCV(
    #     model,
    #     {
    #         "hidden_layer_sizes": [(600,), (700,), (800,)],
    #         "learning_rate": ['constant', 'adaptive'],
    #         "alpha": [0.0, 0.001]
    #     },
    #     n_jobs=16,
    #     verbose=True
    # )
    model = SVC(
        class_weight='balanced',
        C=1.0,
        degree=3,
        gamma="auto"
    )
    clf = GridSearchCV(
        model,
        {
            "kernel": ['poly'],
            "C": [0.01],
            "degree": [7],
            "class_weight": [
                {0: 3, 1: 100, 2: 100},
                {0: 5, 1: 100, 2: 100}
            ],
            #             # "gamma": ['auto', 1, 10]
        },
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

    # model = SVC(kernel='rbf', class_weight='balanced', degree=)
    # model.fit(x_train_scaled, y_train)

    test_output = clf.predict(ttd.x_test_scaled).tolist()
    test_dates = sd.dates[-len(ttd.testing_data):].tolist()

    print(metrics.classification_report(ttd.y_test, test_output))
    print(metrics.confusion_matrix(ttd.y_test, test_output))

    plot(sd, test_dates, test_output)

