"""
For testing purposes only
Usage:
    data_reader blob_name local_file_name

"""
import os
import sys
import uuid
import configuration
from forecaster.datamanager import DataManager
from argparse import ArgumentParser


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-e", "--environment", dest="environment",
                    help="one of: [dev,test,prod]", default="dev")

    parser.add_argument("-t", "--datasourcetype", dest="data_source_type",
                    help="the type of data source [test,azure_blob]", default="azure_blob")

    parser.add_argument("-s", "--datasource", dest="data_source",
                    help="for future use---", default="?")

    parser.add_argument("-c", "--container", dest="container",
                    help="the name of the azure container", default=None)

    parser.add_argument("-d", "--dataset", dest="dataset",
                    help="the name of the azure blob", default="test_dataset.csv")

    parser.add_argument("-o", "--output file", dest="output_file_name",
                    help="full path to output file where data will be copied", default=None)

    return parser.parse_args()


params = parse_arguments()

params.output_file_name = params.output_file_name if params.output_file_name != None else params.dataset
 
if (os.path.isfile(params.output_file_name)):
    print("Output file: {} already exist. Please delete the local file first.".format(params.output_file_name))
    exit()
   
# initialize dev configuration environment
config = configuration.get_configuration(params.environment)

# initlaize the data manager
dm = DataManager(config)

# upoad the file
try:
    df = dm.get_data(data_source_type=params.data_source_type, data_source=params.data_source, dataset=params.dataset, full_path_to_file=params.output_file_name, container=params.container)
    print(df.head())
except Exception as ex:
    print(ex)
    print("Got error: ", ex)
    print("Please ensure the dataset is properly formated. [date] [value]")
    pass

if (os.path.isfile(params.output_file_name)):
    print("File Downloaded: {}".format(params.output_file_name))



