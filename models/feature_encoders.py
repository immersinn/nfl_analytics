
import numpy
import scipy

from sklearn.base import (BaseEstimator, TransformerMixin)
from sklearn.preprocessing import (LabelEncoder, OneHotEncoder, Imputer)
from sklearn.cross_validation import train_test_split

import theano
import theano.tensor as T


class ItemSelector(BaseEstimator, TransformerMixin):
    """For data grouped by feature, select subset of data at a provided key.

    The data is expected to be stored in a 2D data structure, where the first
    index is over features and the second is over samples.  i.e.

    >> len(data[key]) == n_samples

    Please note that this is the opposite convention to sklearn feature
    matrixes (where the first index corresponds to sample).

    ItemSelector only requires that the collection implement getitem
    (data[key]).  Examples include: a dict of lists, 2D numpy array, Pandas
    DataFrame, numpy record array, etc.

    >> data = {'a': [1, 5, 2, 5, 2, 8],
               'b': [9, 4, 1, 4, 1, 3]}
    >> ds = ItemSelector(key='a')
    >> data['a'] == ds.transform(data)

    ItemSelector is not designed to handle data grouped by sample.  (e.g. a
    list of dicts).  If your data is structured this way, consider a
    transformer along the lines of `sklearn.feature_extraction.DictVectorizer`.

    Parameters
    ----------
    key : hashable, required
        The key corresponding to the desired value in a mappable.
    """
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]


class IdentityEncoder():

    def __init__(self, name=None):
        self.name = name
        self.imp = Imputer(missing_values = 'NaN',
                           strategy = 'mean',
                           axis = 0)

    def fit(self, X, y=None):
        X = numpy.array(X).reshape(-1,1)
        self.imp.fit(X)


    def transform(self, X):
        X = numpy.array(X).reshape(-1,1)
        return(self.imp.transform(X))


    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))
    

class NamedCategoryEncoder():
    """Combination of LabelEncoder and OneHotEncoder.
    
    Two encoders are required using the sklearn.preprocessing module
    for converting named categories into one-hit vectors:  the
    LabelEncoder (category names to integers) and OneHotEncoder
    (category integer labels to a vector with a "1" in the category position.
    This class combines those two steps into a single encoder for
    ease of use.

    Additionally, neither LabelEncoder nor OneHotEncoder work in a
    Pipeline or FeatureUnion due to the lack of an explicit "y"
    input. 
    """
    
    def fit(self, category_names, y=None, **kargs):
        names2Ints = LabelEncoder().fit(category_names)
        category_ints = names2Ints.transform(category_names).reshape(-1,1)
        ints2OneHot = OneHotEncoder().fit(category_ints)
        self._n2i = names2Ints
        self._i2oh = ints2OneHot
        
    def transform(self, category_names, **kargs):
        return(self._i2oh.transform(\
                                   self._n2i.transform(category_names)\
                                   .reshape(-1,1)))
    
    def fit_transform(self, category_names, y=None, **kargs):
        self.fit(category_names)
        return(self.transform(category_names))
    
    
class BoolLabelEncWrapper():
    """ Wrapper around the LabelEncoder class to enhance functionality

    Built-in boolean does not work with Pipeline or FeatureUnion because 
    it does not have a designated "y" slot in it's 
    "fit" or "fit_transform" methods. 

    Additionally, the default return object from LabelEncoder's 
    "fit_transform" method is not compatiable with 
    the default return object from OneHotEncoder class.  Thus,
    we also reshape the object to force a row vector.

    """
    
    def fit(self, X, y=None):
        self.model = LabelEncoder()
        self.model.fit(['True', 'False'])
        
    def transform(self, X):
        return(self.model.transform(X).reshape(-1,1))
    
    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))
