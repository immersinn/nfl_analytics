

import numpy
import pandas
import sklearn

import statsmodels.api as sm
from statsmodels.formula.api import ols, gls, wls
from patsy import PatsyError


class MeanModel():
    """
    Build a model that simply calculates the overall mean porints value
    """
    
    def fit(self, X, y=None):
        self.model = X.points.mean()
        
    def transform(self, X):
        return(numpy.array([self.model for _ in range(X.shape[0])]))
    
    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))



class MeanCatModel():
    """
    Calculate the mean value for a particular category.
    Return that value for all players in that category.
    """
    
    def __init__(self, category):
        self.cat = category
    
    def fit(self, X, y=None):
        self.model = {}
        for val in pandas.unique(X[self.cat]):
            table = X[X[self.cat]==val]
            self.model[val] = table.points.mean()
        self.model_backup = X.points.mean()
        
    def transform(self, X):
        out = []
        for i, row in X.iterrows():
            try:
                out.append(self.model[row[self.cat]])
            except KeyError:
                out.append(self.model_backup)
        return(numpy.array(out))
    
    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))


class RegressionModelSimple():
    """
    Build a model / glm model based on a formula.
    """

    _allowed_models = ['ols', 'wls', 'gls']

    def __init__(self, model_type, formula):
        if model_type not in self._allowed_models:
            err_msg = "Unsupported model - %s - provided; use one of: (%s)" % \
                      (model_type, str(self._allowed_models))
            raise ValueError(err_msg)
        self.model_type = model_type
        self.formula = formula


    def fit(self, X, y=None):
        self.model = {'ols' : ols,
                      'wls' : wls,
                      'gls' : gls}[self.model_type](self.formula,
                                                    data=X).fit()


    def transform(self, X):
        y_ = self.model.predict(X)
        return(y_)


    def fit_transform(self, X, y=None):
        self.fit(X)
        return(self.transform(X))
    
        
