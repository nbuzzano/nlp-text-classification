import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot  as plt

from sklearn.model_selection import learning_curve
from sklearn.model_selection import validation_curve
from sklearn.model_selection import ShuffleSplit, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def plot_learning_performance(regressor, X, y):

    """
    Draw a graph that visualizes the learning curves of the model for both
     training and testing as the size of the training set is increased. 
     
     Note that the shaded region of a learning curve denotes the uncertainty 
     of that curve (measured as the standard deviation). 

     The model is scored on both the training and testing sets using R2, the coefficient of determination.
    """
    
    # Create 10 cross-validation sets for training and testing
    cv = ShuffleSplit(n_splits = 5, test_size = 0.2, random_state = 0)
    cv.get_n_splits(X)

    # Generate the training set sizes increasing by 50
    train_sizes = np.rint(np.linspace(1, X.shape[0]*0.8 - 1, 9)).astype(int)

    # Calculate the training and testing scores
    sizes, train_scores, test_scores = learning_curve(regressor, X, y, \
        cv = cv, train_sizes = train_sizes, scoring = 'r2')

    # Find the mean and standard deviation for smoothing
    train_std = np.std(train_scores, axis = 1)
    train_mean = np.mean(train_scores, axis = 1)
    test_std = np.std(test_scores, axis = 1)
    test_mean = np.mean(test_scores, axis = 1)

    from matplotlib.pyplot import figure
    figure(num=None, figsize=(8, 5), dpi=80, facecolor='w', edgecolor='k')

    plt.title('')
    plt.xlabel('Number of Training Points')
    plt.ylabel('r2 score')
    plt.xlim([0, X.shape[0]*0.8])
    plt.ylim([-0.05, 1.05])

    plt.plot(sizes, train_mean, 'o-', color = 'r', label = 'Training Score')
    plt.plot(sizes, test_mean, 'o-', color = 'g', label = 'Testing Score')
    plt.fill_between(sizes, train_mean - train_std, \
        train_mean + train_std, alpha = 0.15, color = 'r')
    plt.fill_between(sizes, test_mean - test_std, \
        test_mean + test_std, alpha = 0.15, color = 'g')

    # Visual aesthetics
    plt.legend(bbox_to_anchor=(0.4, 1.3), loc='lower left', borderaxespad = 0.)

    plt.suptitle(type(regressor).__name__ + ' Learning Performances', fontsize = 16, y = 1.03)
    plt.show()

def predict_trials(X, y, model, data):
    """ Performs trials of fitting and predicting data. 
        
        Sensitivity :: Run the code cell below to run the fit_model function ten times 
        with different training and testing sets to see how the prediction for
        a specific client changes with respect to the data it's trained on.

    """

    # Store the predicted prices
    prices = []

    for k in range(10):
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, \
            test_size = 0.2, random_state = k)
        
        # Fit the data
        #reg = fitter(X_train, y_train)
        model.fit(X_train, y_train)
        reg = model
        
        # Make a prediction
        pred = reg.predict([data])[0]
        prices.append(pred)
        
        # Result
        print("Trial {}: {:,.2f}".format(k+1, pred))

    # Display price range
    print("\nRange in values: {:,.2f}".format(max(prices) - min(prices)))

def test_print():
    print('test print')



