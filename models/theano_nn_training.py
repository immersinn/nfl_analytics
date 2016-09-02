
import os
import time

import numpy
import scipy

import theano
import theano.tensor as T


def generalTrainer(datasets, nn_object,
                   n_epochs=100, batch_size=10,
                   patience=1000, patience_increase=2, improvement_threshold=0.995,
                   ):

    #####
    ###  Create Pointers to NN attributes
    #####

    test_error_func     = nn_object.test_error
    train_error_func    = nn_object.train_error
    cost                = nn_object.cost
    updates             = nn_object.updates
    rng                 = nn_object.rng
                 

    #####
    ###  Prepare the functions, data for training the NN
    #####
    
    # Unwrap data
    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    test_set_x, test_set_y = datasets[2]


    # compute number of minibatches for training, validation and testing
    n_train_batches = int(numpy.ceil(train_set_x.get_value(borrow=True).shape[0] / batch_size))
    if valid_set_x is not None:
        n_valid_batches = int(numpy.ceil(valid_set_x.get_value(borrow=True).shape[0] / batch_size))
    n_test_batches = int(numpy.ceil(test_set_x.get_value(borrow=True).shape[0] / batch_size))


    # Model Dummy Variuables
    index = T.lscalar()  # index to a [mini]batch
    x = nn_object.x  # the data is presented as rasterized images
    y = nn_object.y  # the labels are presented as 1D vector of
                        # [int] labels


    # Build test function
    test_model = theano.function(inputs=[index],
                outputs=test_error_func(y),
                givens={
                    x: test_set_x[index * batch_size:(index + 1) * batch_size],
                    y: test_set_y[index * batch_size:(index + 1) * batch_size]})

    # Build valid function
    valid_model = theano.function(inputs=[index],
                 outputs=train_error_func(y),
                 givens={
                     x: valid_set_x[index * batch_size:(index + 1) * batch_size],
                     y: valid_set_y[index * batch_size:(index + 1) * batch_size]})

    # Build train function
    train_model = theano.function(inputs=[index], outputs=cost,
                updates=updates,
                givens={
                    x: train_set_x[index * batch_size:(index + 1) * batch_size],
                    y: train_set_y[index * batch_size:(index + 1) * batch_size]})


    #####
    ###  Train the model
    #####
    
    # early-stopping parameters
    patience = patience  # look as this many examples regardless
    patience_increase = \
                      patience_increase  # wait this much longer when a new best is
                           # found
    improvement_threshold = \
                          improvement_threshold # a relative improvement of this much is
                                   # considered significant
    validation_frequency = min(n_train_batches, patience / 2)
                                  # go through this many
                                  # minibatche before checking the network
                                  # on the validation set; in this case we
                                  # check every epoch

    best_params = None
    best_validation_loss = numpy.inf
    best_iter = 0
    test_score = 0.
    start_time = time.clock()

    epoch = 0
    done_looping = False

    while (epoch < n_epochs) and (not done_looping):
        
        epoch = epoch + 1
        
        for minibatch_index in range(n_train_batches):

            minibatch_avg_cost = train_model(minibatch_index)
            # iteration number
            iteration = (epoch - 1) * n_train_batches + minibatch_index

            if (iteration + 1) % validation_frequency == 0:

                # test it on the test set
                validation_losses = [valid_model(i) for i
                                     in range(n_valid_batches)]
                this_validation_loss = numpy.mean(validation_losses)

                if this_validation_loss < best_validation_loss:
                    
                    if this_validation_loss < (best_validation_loss *  \
                                               improvement_threshold):
                        patience = max(patience, 
                                       iteration * patience_increase)
                            
                    best_validation_loss = this_validation_loss
                    best_iter = iteration

                test_losses = [test_model(i) for i
                               in range(n_test_batches)]
                test_score = numpy.mean(test_losses)

                print(('     epoch %i, minibatch %i/%i, test error of '
                       'best model %0.5f') %
                      (epoch, minibatch_index + 1,
                       n_train_batches,
                       test_score))

            if patience <= iteration:
                done_looping = True
                break

    end_time = time.clock()
    print(('Optimization complete. Best validation score of %0.5f '
           'obtained at iteration %i, with test performance %0.5f') %
          (best_validation_loss, best_iter + 1, test_score))
    print('The code for file ' +
          ' ran for %.2fm' % ((end_time - start_time) / 60.))
