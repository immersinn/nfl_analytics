
import numpy
import scipy

import theano
import theano.tensor as T

from sklearn.pipeline import (Pipeline, FeatureUnion)

from .feature_encoders import (ItemSelector, IdentityEncoder,
                               NamedCategoryEncoder, BoolLabelEncWrapper)



def buildFeatureEncoder(X, window):
    # Various column names
    ha_cols = [n for n in X.columns \
               if n.find('is_home_') > -1]
    team_cols = ['team']
    team_cols.extend([n for n in X.columns \
                      if n.find('opponent') > -1])
    points_cols = [n for n in X.columns \
                   if n.find('points_') > -1]
    _ = points_cols.pop(points_cols.index('points_' + str(window)))
    week_cols = [n for n in X.columns \
                   if n.find('week_') > -1]

    # Fit team encoder
    team_encoder = NamedCategoryEncoder()
    team_encoder.fit(X[team_cols].unstack())

    # Set up FeatureUnion
    enc_lookup = [(ha_cols, BoolLabelEncWrapper()),
                  (team_cols, team_encoder),
                  (points_cols, IdentityEncoder()),
                  (week_cols, IdentityEncoder()),
                  (['season'], NamedCategoryEncoder())
                  ]
    transformer_list = []
    for cols,enc in enc_lookup:
        for col in cols:
            transformer_list.append(
                (col, Pipeline([
                    ('selector', ItemSelector(key=col)),
                    ('one_hot',  enc),
                    ]))
            )
    feature_encoder = FeatureUnion(
        transformer_list=transformer_list
    )
    feature_encoder.fit(X);
    return(feature_encoder)


def genTrainTest(data, feature_encoder, window, test_size=3):
    
    # The test data should be the last n weeks for every player
    n_records = data.shape[0]
    y_label = "points_" + str(window)
    y = numpy.array(data[y_label])
    
    # Get train, test indexes
    train_indxs, valid_indxs, test_indxs = last_n_weeks_test_train(data,
                                                                   test_size)
    
    # Transform X data
    X = feature_encoder.transform(data).toarray()
    n_features = X.shape[1]
    
    # Package Test, Train data
    X_train = X[train_indxs,]
    y_train = [y[i] for i in train_indxs]
    X_valid = X[valid_indxs,]
    y_valid = [y[i] for i in valid_indxs]
    X_test = X[test_indxs,]
    y_test = [y[i] for i in test_indxs]
    
    train_set = (X_train, y_train)
    valid_set = (X_valid, y_valid)
    test_set = (X_test, y_test)
    
    # Covert the data to Theano shared
    train_set_x, train_set_y = shared_dataset(train_set)
    valid_set_x, valid_set_y = shared_dataset(valid_set)
    test_set_x, test_set_y = shared_dataset(test_set)
    
    rval = [(train_set_x, train_set_y), 
            (valid_set_x, valid_set_y),
            (test_set_x, test_set_y)]
    
    return(rval, n_features)


def last_n_weeks_test_train(X, n):
    X.index = range(X.shape[0])
    train_indxs = []
    valid_indxs = []
    test_indxs = []
    for pid in numpy.unique(X.pid):
        sub = X[X.pid == pid]
        count = sub.shape[0]
        test_indxs.extend(list(sub.index)[-n:])
        valid_indxs.append(int(sub.index[-(n+1)]))
        train_indxs.extend(list(sub.index)[:(count-n-1)])
    
    return(train_indxs, valid_indxs, test_indxs)


def shared_dataset(data_xy, borrow=True):
    """ Function that loads the dataset into shared variables

    The reason we store our dataset in shared variables is to allow
    Theano to copy it into the GPU memory (when code is run on GPU).
    Since copying data into the GPU is slow, copying a minibatch everytime
    is needed (the default behaviour if the data is not in a shared
    variable) would lead to a large decrease in performance.
    """
    data_x, data_y = data_xy
    shared_x = theano.shared(numpy.asarray(data_x,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    shared_y = theano.shared(numpy.asarray(data_y,
                                           dtype=theano.config.floatX),
                             borrow=borrow)
    # When storing data on the GPU it has to be stored as floats
    # therefore we will store the labels as ``floatX`` as well
    # (``shared_y`` does exactly that). But during our computations
    # we need them as ints (we use labels as index, and if they are
    # floats it doesn't make sense) therefore instead of returning
    # ``shared_y`` we will have to cast it to int. This little hack
    # lets ous get around this issue
    return shared_x, T.cast(shared_y, 'int32')
