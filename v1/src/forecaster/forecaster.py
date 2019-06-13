"""
   Base Forecasting Class
   See also arima_forecaster.py, ets_forecaster.py 
"""
__version__ = "0.1.0"
from abc import ABC, ABCMeta, abstractmethod
import pandas as pd
import numpy as np
import datetime
import calendar

from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error


class Forecaster(ABC):
    """
    Base class for Forecasters.
    EtsForecaster, ArimaForcaster and other Forectasers to be implemented in the future should 
    be derived from this class.
    """
    def __init__(self):
        self._model = None

    @property 
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @abstractmethod
    def version(self):
        return __version__

    @abstractmethod
    def analysis(self, y_train):
        """determines wether the timeseries can be used with this model
        
        Arguments:
            y_train {[timeseries]} -- [training data]
        
        Returns:
            [type] -- [description]
        """

        adf = adfuller(y_train)

        print('ADF Statistic: %f' % adf[0])
        print('p-value: %f' % adf[1])
        print('Critical Values:')
        for key, value in adf[4].items():
            print('\t%s: %.3f' % (key, value))
        
        
        stationary = adf[0] < adf[4]["5%"]
        
        return {'stationary': stationary}
    
    @classmethod
    def mae(self, y_hat, y_true):
        return mean_absolute_error(y_true, y_hat)

    @abstractmethod
    def train(self, y_train, order, seasonal_order):
        pass        
        
    @abstractmethod
    def save(self, dest):
        pass

    @abstractmethod
    def load(self, source):
        pass

    @abstractmethod
    def forecast(self, periods=1):
        return self.model.forecast(periods)


if __name__ == '__main__':
  print("Base Forecasting Class")

    