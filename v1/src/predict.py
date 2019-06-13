import os
import sys
import uuid
import configuration
import json
import pandas as pd

from forecaster.forecaster_factory import ForecasterFactory
from forecaster.datamanager import DataManager
from argparse import ArgumentParser

"""
This module loads and ARIMA model and outputs a forecast.


"""

class Predict():

    """
        This class wraps all the functionality related to creating a forecast including:
            ()fetching the data.
            ()re-training the model
            -loading the model
            -forecasting
    """

    def forecast(self, config, data_source_type, data_source, model_name, output_name, periods=12):
        dm = DataManager(config)

        if (data_source_type=="azure_blob"):
            # fetch the model pckl file
            blob_name=model_name
            local_path=dm.get_temporary_folder()
            
            # use a random name to avoid attacks - someone could overwrite a critical file 
            local_file_name ="Model_" + str(uuid.uuid4()) + ".mdl"
            full_path_to_file =os.path.join(local_path, local_file_name)
            dm.get_model_file(full_path_to_file, blob_name)
    
            # load the model from the file
            f = ForecasterFactory.load_model(full_path_to_file)
    
            # create the forecast
            forecast_df = f.forecast(periods)

  
            # store results as json
            forecast_json = forecast_df.to_json(date_format='iso')
            data = '{"forecast": ' + forecast_json + '}'
            dm.save_result( blob_name + "-prediction.json", data)
            # store results as csv
            forecast_csv = forecast_df.to_csv()
            forecast_csv = forecast_csv
            dm.save_result( blob_name + "-prediction.csv", forecast_csv)

            # remove local file
            os.remove(full_path_to_file)
            return forecast_df

#        elif data_source_type = "test":


        return 

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-e", "--environment", dest="environment",
                    help="one of: [dev,test,prod]", default="dev")

    parser.add_argument("-t", "--datasourcetype", dest="data_source_type",
                    help="the type of data source [test,azure_blob]", default="azure_blob")

    parser.add_argument("-s", "--datasource", dest="data_source",
                    help="for future use---", default="?")

    parser.add_argument("-m", "--model", dest="model_name",
                    help="name of the model", required=True)

    parser.add_argument("-o", "--output", dest="output_name",
                    help="name of output blob that will contain the forecast", default=None)

    parser.add_argument("-p", "--periods", dest="periods",
                    help="Number of periods", type=int, default=12)

    parser.add_argument("-g", "--graph plot", dest="plot_graph",
                    help="Plot a graph with results (y/n)", default="n")

    #parser.add_argument("-d", "--dataset", dest="dataset",
    #                help="the name of the azure blob", required=True)

    return parser.parse_args()


if __name__ == '__main__':
    
    params = parse_arguments()

    config = configuration.get_configuration(params.environment)

    print ("Configuration   :", config)
    print ("Data Source Type:", params.data_source_type)
    print ("Data Source.....:", params.data_source)
    print ("Model Name......:", params.model_name)
    print("Periods..........:", params.periods)

    forecast = Predict().forecast(config = config, data_source_type=params.data_source_type, data_source=params.data_source, 
                            model_name=params.model_name, periods=params.periods, output_name=params.output_name)
    print(forecast)
    
    if (params.plot_graph=="y"):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8,12))
        plt.grid(True)
        plt.plot(forecast)
        plt.savefig("graph.png")
        plt.show()
