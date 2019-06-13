"""
For testing purposes only
Usage:
    data_uploader local_file_name

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

    parser.add_argument("-i", "--input file", dest="input_file_name",
                    help="full path to csv file to upload", default=None, required=True)

    parser.add_argument("-d", "--dataset", dest="dataset",
                    help="the name of the azure blob", default=None)

    return parser.parse_args()


params = parse_arguments()

if (not os.path.isfile(params.input_file_name)):
    print("File: {} does not exist".format(params.input_file_name))
    exit()
    
params.dataset = params.dataset if params.dataset != None else params.input_file_name

# initialize dev configuration environment
config = configuration.get_configuration("dev")

# initlaize the data manager
dm = DataManager(config)

# upoad the file
dm.save_data(params.data_source_type, None, params.input_file_name, params.dataset)

print("The file: {} was uploaded to the blob: {}".format(params.input_file_name, params.dataset ))
print("The storage account is: {} {}".format(config.storage_account, config.data_container_name) )


