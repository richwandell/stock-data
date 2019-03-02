import sys

from sklearn.svm import SVC

sys.path.append("..")
from sklearn.neural_network import MLPClassifier
from utils.portfolio_predict_utils import make_max_sharpe_dataset, make_training_testing_datasets, plot
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
    df, df_source, dates, maxes_dates, maxes_vals, mins_dates, mins_vals, target = make_max_sharpe_dataset()
    # data is now fully collected for all assets in the portfolio including
    x_train_scaled, y_train, x_test_scaled, x_test, y_test, testing_data = make_training_testing_datasets(df)

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
            "kernel": ['poly', 'rbf', 'sigmoid'],
            "C": [0.1, 1.0],
            "degree": [3, 5, 7],
            #             # "gamma": ['auto', 1, 10]
        },
        n_jobs=14,
        verbose=True
    )
    clf.fit(x_train_scaled, y_train)
    # Best paramete set
    print('Best parameters found:\n', clf.best_params_)

    # All results
    means = clf.cv_results_['mean_test_score']
    stds = clf.cv_results_['std_test_score']
    for mean, std, params in zip(means, stds, clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

    # model = SVC(kernel='rbf', class_weight='balanced', degree=)
    # model.fit(x_train_scaled, y_train)

    test_output = clf.predict(x_test_scaled).tolist()
    test_dates = dates[-len(testing_data):].tolist()

    print(metrics.classification_report(y_test, test_output))
    print(metrics.confusion_matrix(y_test, test_output))

    plot(df_source, dates, target, maxes_dates, maxes_vals, mins_dates, mins_vals, test_dates, test_output)

