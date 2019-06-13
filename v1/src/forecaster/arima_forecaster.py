"""[summary]
    Forecasting module 
    This module uses ARIMA to train a model and create a forecast.

    https://www.kaggle.com/berhag/co2-emission-forecast-with-python-seasonal-arima
    https://machinelearningmastery.com/time-series-forecast-case-study-python-monthly-armed-robberies-boston/
    https://medium.com/@josemarcialportilla/using-python-and-auto-arima-to-forecast-seasonal-time-series-90877adff03c

"""
__version__ = "0.1.0"

import pandas as pd
import numpy as np
import datetime
import calendar

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMAResults
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error
from pyramid.arima import auto_arima

import warnings
import itertools
from forecaster.forecaster import Forecaster
#from forecaster import Forecaster

class ArimaForecaster(Forecaster):
    """
    Implements:
        train() trains an ARIMA model for forecasting
        forecast() returns a forecast 
        
        predict() same as forecast
    """
    def __init__(self):
        super().__init__()

    def version(self):
        return __version__

    def analysis(self, y):
        """determines wether the timeseries can be used with this model
        
        Arguments:
            y_train {[timeseries]} -- [training data]
        
        Returns:
            [type] -- [description]
        """
        base_analysis = super().analysis(y)
        num_periods = 12

        y_train = y[0: -num_periods]
        
        #order, seasonal_order = self.grid_search(y_train, max_order=(12,2,2,12,2,2,12), progress=lambda x: print(x))

        self.train(y_train) #, order, seasonal_order)
        y_hat = self.forecast(num_periods)["value"]
        y_true = y_train[-num_periods:]
        base_analysis['mae'] = self.mae(y_true, y_hat)
        base_analysis['model_params'] = self.model_params
        
        return base_analysis

        


    def train(self, y_train, order=None, seasonal_order=None):
        
        # y_train: training dataset
        # order: ARIMA order. Example: (1,1,0)
        # seasonal: ARIMA seasonal order. Example: (0,1,0)
        stepwise_model = auto_arima(y_train, start_p=0, start_q=1,
                                max_p=6, max_q=3, m=12,
                                start_P=0, seasonal=True,
                                #d=1, D=1, 
                                trace=True,
                                error_action='ignore',  
                                suppress_warnings=True, 
                                stepwise=True) #.fit(y_train)

        warnings.filterwarnings("ignore") # specify to ignore warning messages
        self.model = sm.tsa.statespace.SARIMAX(y_train,
                                        order=stepwise_model.order,
                                        seasonal_order=stepwise_model.seasonal_order,
                                        enforce_stationarity=False,
                                        enforce_invertibility=False
                                        ).fit(disp=False)
        
        self.model_params = (stepwise_model.order, stepwise_model.seasonal_order)
        

        return self.model
        
    def grid_search(self, y_train, max_order=(12,1,1,1,1,1,12), progress=None, error_eval=None):
        """Returns the order of the ARIMA model with the lowest AIC
        
        Arguments:
            y_train {[Series]} -- [Single value Timeseries indexed by time. ]
        
        Keyword Arguments:
            max_order {tuple} -- The maximum PDQ,pdq order for the ARIMA model (default: {(12,1,1,1,1,1,12)})
            progress {[type]} -- Optional callback to track progrsss (default: {None})
        
        Returns:
            [tuple] -- [ARIMA PDQpdq parameters]
        """

        warnings.filterwarnings("ignore") # specify to ignore warning messages
        min_error = 1E25
        min_params = (-1,-1,-1,0,0,0)
        
        param_range = pdqPDQ(max_order) 

        for order,seasonal_order in param_range:
            try:
                model = self.train(y_train, order, seasonal_order)
                error = 0
                if (error_eval != None):
                    error = error_eval(model)
                else:
                    error = model.aic

                if error < min_error:
                    min_error = error
                    min_params = order, seasonal_order

                if (progress != None):
                    progress((min_params, order, seasonal_order, error))
                
            except ValueError as e:
                #print("ex", type(e))
                continue

        return min_params
    
    def save(self, dest):
        # save model
        return self.model.save(dest)
    
    @staticmethod
    def load(source):
        # load model
        f = ArimaForecaster()
        f.model = ARIMAResults.load(source)
        return f

    def forecast(self, periods=1):
        result = self.model.get_forecast(periods)

        # create stanard dataframe with forecast and conf. intervals
        forecast_df = pd.concat([result.predicted_mean, result.conf_int()], axis=1)
        forecast_df.index.name = "date"
        forecast_df.columns = ["value","low","high"]
        
        return forecast_df


def pdqPDQ(o):
    for p in range(0, o[0]+1):
        for d in range(0,o[1]+1):
            for q in range(0,o[2]+1):
                for P in range(0,o[3]+1):
                    for D in range(0, o[4]+1):
                        for Q in range(0, o[5]+1):
                            yield (p,d,q),(P,D,Q,12)



if __name__ == '__main__':

    print("Version: {}".format(__version__))
    
    co2 = pd.DataFrame(sm.datasets.co2.load().data)
    co2["date"] = co2["date"].apply(lambda b: datetime.datetime(int(b[0:4]),int(b[4:6]),int(b[6:])))
    co2 = co2.set_index('date')
    co2 = co2.resample('MS').mean()
    co2 = co2.fillna(co2.bfill())

    f = ArimaForecaster()

    y_train = co2["co2"]
    print(f.analysis(y_train))
    
    #order, seasonal_order = f.grid_search(y_train, max_order=(0,0,0,0,1,1,12), progress=lambda x: print(x))

    #print("\n","Optimal Order: ARIMA {} {}".format(order,seasonal_order))

    model = f.train(y_train) #, order, seasonal_order)

    print(f.forecast(2))

    f.save("co2.mdl")

    f2 = f.load("co2.mdl")
    print(f2.forecast(2))
    
    print(f'mae: {f.mae(y_train[-12:], f2.forecast(12)["value"])}')
    
    