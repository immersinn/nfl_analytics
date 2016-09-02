
import numpy
import scipy
import pandas

import theano
import theano.tensor as T



class HiddenLayer():
    
    def __init__(self, x_input, rng, n_in, n_out, name, activation=None):
        
        # Initilize the shared variables W and b
        W_values = numpy.asarray(rng.uniform(
                low=-numpy.sqrt(6. / (n_in + n_out)),
                high=numpy.sqrt(6. / (n_in + n_out)),
                size=(n_in, n_out)), dtype=theano.config.floatX)
        if activation == theano.tensor.nnet.sigmoid:
            W_values *= 4

        W_values = numpy.zeros(shape=(n_in, n_out))

        b_values = numpy.zeros((n_out,),
                               dtype=theano.config.floatX)

        W = theano.shared(value=W_values, 
                          name=name + '_W',
                          borrow=True)
        b = theano.shared(value=b_values,
                          name=name + '_b',
                          borrow=True)
        
        # Associated params with object
        self.W = W; self.b = b;
        self.params = [W, b]
        
        # Output
        lin_output = T.dot(x_input, W) + b
        output = lin_output if activation is None \
                 else activation(lin_output)
        self.output = output


class MLPBuilder():

    def __init__(self, n_features=0,
                 x_in_placeholder=T.matrix('x'), y_in_placeholder=T.ivector('y'),
                 layers_dict={},
                 learning_rate=0.01, L1_reg=0.00, L2_reg=0.001,
                 rng=numpy.random.RandomState(8675309),
                 ):


        # Temporary declare layer variables here
        n_in = n_features
        n_hidden = 256
        n_out = 1
        x = x_in_placeholder
        y = y_in_placeholder

        # Temporary hard coded layer construction
        hidden01 = HiddenLayer(x, rng,
                               n_in=n_features, n_out=n_hidden, name='hidden01',
                               activation=theano.tensor.nnet.sigmoid)
        hidden02 = HiddenLayer(hidden01.output, rng,
                               n_in=n_hidden, n_out=1, name='hidden02',
                               activation=None)
        y_given_x = hidden02.output
        params = hidden01.params + hidden02.params


        # Error calculations (sum of sq error)
        def error(y):
            return((T.sum(T.sqr(y_given_x.transpose() - y))) / y.shape[0])

        def error_eval(y):
            return((T.sum(T.sqr(y_given_x.transpose() - y))) / y.shape[0])


        # Cost function
        L1 = abs(hidden01.W).sum() + \
             abs(hidden02.W).sum()
        L2 = (hidden01.W ** 2).sum() + \
             (hidden02.W ** 2).sum()

        cost = error(y) + \
               L1_reg * L1 + \
               L2_reg * L2


        # Calculate Gradients, Updates
        gparams = []
        for param in params:
            gparam = T.grad(cost, param)
            gparams.append(gparam)

        updates = []
        for param, gparam in zip(params, gparams):
            updates.append((param, param - learning_rate * gparam))


        # Assign stuff from above as attrs
        self.test_error = error_eval
        self.train_error = error
        self.cost = cost
        self.updates = updates
        self.rng = rng
        self.x = x
        self.y = y


