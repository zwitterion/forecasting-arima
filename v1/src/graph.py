"""
For testing purposes only
Usage:
    graph datasetname prediction-csv-blob

"""
import os
import sys
import uuid
import configuration
from forecaster.datamanager import DataManager
from argparse import ArgumentParser
import matplotlib.pyplot as plt

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-e", "--environment", dest="environment",
                    help="one of: [dev,test,prod]", default="dev")

    parser.add_argument("-t", "--datasourcetype", dest="data_source_type",
                    help="the type of data source [test,azure_blob]", default="azure_blob")

    parser.add_argument("-s", "--datasource", dest="data_source",
                    help="for future use---", default="?")

    parser.add_argument("-d", "--dataset", dest="dataset",
                    help="the name of the azure blob containing the timeseries", required=True)

    parser.add_argument("-p", "-prediction", dest="prediction_dataset",
                    help="the name of the azure blob containing the prediction", required=True)

    return parser.parse_args()


params = parse_arguments()

# initialize dev configuration environment
config = configuration.get_configuration(params.environment)

# initlaize the data manager
dm = DataManager(config)

# get the timeseries data
timeseries = None
prediction = None
try:
    timeseries = dm.get_data(data_source_type=params.data_source_type, data_source=params.data_source, dataset=params.dataset, full_path_to_file=None)
    print(timeseries.head())

    prediction = dm.get_data(data_source_type=params.data_source_type, data_source=params.data_source, dataset=params.prediction_dataset, full_path_to_file=None, container=config.results_container_name)
    print(prediction.head())

except Exception as ex:
    print(ex)
    print("Got error: ", ex)
    print("Please ensure the dataset is properly formated. [date] [value]")
    exit

plt.figure(figsize=(8,10))
plt.plot(timeseries, label="observed", color="lightblue")

plt.plot(prediction["low"], label="low", color="gray", alpha=0.5)
plt.plot(prediction["high"], label="high", color="gray", alpha=0.5)
ax = plt.gca()
# fill area between confidence intervals
ax.fill_between(prediction.index,
                prediction["low"],
                prediction["high"], color='k', alpha=.25)
# plot predicted values                
plt.plot(prediction["value"], label="forecast", color="green")


plt.plot([timeseries.iloc[-1].name, prediction.iloc[0].name], [timeseries.iloc[-1][0], prediction.iloc[0][0]] )

plt.title("Observed and Forecasted Values")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
plt.show()




