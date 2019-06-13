"""[summary]
    Forecasting module 
    This module uses ETS to train a model and create a forecast.
    
    http://www.statsmodels.org/dev/tsa.html

"""
__version__ = "0.1.0"

import pandas as pd
import numpy as np
import datetime
import calendar

from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.holtwinters import HoltWintersResults, HoltWintersResultsWrapper
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error
import warnings
import itertools
from forecaster.forecaster import Forecaster
#from forecaster import Forecaster

class EtsForecaster(Forecaster):
    """
    Implements:
        train() method to train an ETS model for forecasting
        forectast() returns a forecast 
        
        predict() same as forecast
    """
    def __init__(self):
        super().__init__()

    def version(self):
        return __version__

    def analysis(self, y):
        """determines wether the timeseries can be used with this model
        
        Arguments:
            y {[timeseries]} -- [training data]
        
        Returns:
            [type] -- [description]
        """
        base_analysis = super().analysis(y)
        num_periods = 12

        y_train = y[0: -num_periods]
        self.train(y_train)
        y_hat = self.forecast(num_periods)["value"]
        y_true = y_train[-num_periods:]
        base_analysis['mae'] = self.mae(y_true, y_hat)
        base_analysis['model_params'] = self.model_params

        return base_analysis
    
    #def mae(self, y_hat, y_true):
    #    return mean_absolute_error(y_true, y_hat)
  
    def train(self, y_train, hyper1=None, hyper2=None):
        
        # y_train: training dataset

        # use_basinhopping=True could produce better results but takes much longer.
        self.model = ExponentialSmoothing(y_train, trend='add', seasonal='add', seasonal_periods=12).fit(optimized=True, use_basinhopping=False)
        #self.model = l.fit(smoothing_level=alpha, smoothing_slope=beta,
        #                smoothing_seasonal=gamma)
        self.model_params = (1,2,3)

        return self.model
        
    def grid_search(self, y_train, max_order=None, progress=None, error_eval=None):
        """Returns the order of the optimal ETS model
        
        Arguments:
            y_train {[Series]} -- [Single value Timeseries indexed by time. ]
        
        
        Returns:
            [tuple] -- 
        """
        return None, None
    
    def save(self, dest):
        # save model
        return self.model.save(dest)

    @staticmethod
    def load(source):
        # load model
        f = EtsForecaster()
        f.model = HoltWintersResultsWrapper.load(source)
        return f
    
    def forecast(self, periods=1):
        result = self.model.forecast(periods)

        # create stanard dataframe with forecast and conf. intervals
        # todo: replace last to 'result' with conf intervals. See ArimaForecast.
        forecast_df = pd.concat([result, result, result], axis=1)
        forecast_df.index.name = "date"
        forecast_df.columns = ["value","low","high"]
        
        return forecast_df


def abg(o):
    for alpha in range(0, 1.0, 0.1):
        for beta in range(0, 1.0, 0.1):
            for gamma in range(0, 1.0, 0.1):
                yield (alpha, beta, gamma)



if __name__ == '__main__':

    print("Version: {}".format(__version__))
    
    co2 = pd.DataFrame(sm.datasets.co2.load().data)
    co2["date"] = co2["date"].apply(lambda b: datetime.datetime(int(b[0:4]),int(b[4:6]),int(b[6:])))
    co2 = co2.set_index('date')
    co2 = co2.resample('MS').mean()
    co2 = co2.fillna(co2.bfill())

    f = EtsForecaster()

    y_train = co2["co2"][0:-12]
    print(f.analysis(y_train))
    
    #order, seasonal_order = f.grid_search(y_train, max_order=(3,1,1,1,1,1,12), progress=lambda x: print(x))

    #print("\n","Optimal Order: ARIMA {} {}".format(order,seasonal_order))

    model = f.train(y_train)

    print(f.forecast(12))

    f.save("co2.mdl")

    f2 = f.load("co2.mdl")
    print(f2.forecast(12)["value"])

    print(f'mae: {f.mae(y_train[-12:], f2.forecast(12)["value"])}')
    


    