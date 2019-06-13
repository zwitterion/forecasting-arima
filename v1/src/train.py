import os
import sys
import uuid
from multiprocessing import Process, Queue
from datetime import datetime
import time
from ast import literal_eval
import json 

import configuration

from forecaster.forecaster_factory import ForecasterFactory
from forecaster.datamanager import DataManager
from argparse import ArgumentParser
import queue

"""
This module trains an ARIMA model agains the specified training data set.

Data is fecthed by the datamanger class.
The evaluation metric is AIC. 
This module does not evaluate metrics on a test dataset...(todo)

"""

class Trainer():

    """
        This class wraps all the functionality related to traing a model including:
            fetching the data.
            hyperparameter tuning
            training the model
            -evaluating the model
            -storing the model
    """

    def start_training(self, env, data_source_type, data_source, dataset, model_name, model_type="arima,ets"):
        """Trains ets and ariam models in parallel
           Sets the best perfoming model as current model
        
        Arguments:
            env {[type]} -- [description]
            data_source_type {[type]} -- [description]
            data_source {[type]} -- [description]
            dataset {[type]} -- [description]
            model_name {[type]} -- 
        
        Keyword Arguments:
            model_type {str} -- [description] (default: {"arima,ets"} ignored for now...)
        """

        # create a queue to get results from each proecess
        q = Queue()

        # start trainers
        p_list = [ Process(target=self.train, args=[q, env, data_source_type, data_source, dataset, model_name + "-" + p_type, p_type]) for p_type in ['arima', 'ets'] ]
        for p in p_list:
            p.start()
            
        for p in p_list:
            p.join()

        min_error = 1e20
        best_model = None
        for p in p_list:
            try:
                r = q.get(timeout=60)
            except Queue.Empty:
                print("Queue is empty. A forecaster task did not terminate properly.")
                break

            mae = r[0].get('mae')
            if (mae < min_error):
                min_error = mae
                best_model = r[0]
            print (r)

        print(f'\nBEST MODEL {best_model}')
        config = configuration.get_configuration(env)
        dm = DataManager(config)
        dm.activate_model(best_model.get('model_name'), model_name)

        return

    def train(self, q, env, data_source_type, data_source, dataset, model_name, model_type):

        print(f'starting {model_type}')
        
        config = configuration.get_configuration(env)
        dm = DataManager(config)

        # fetch the training data set
        y_train = dm.get_data(data_source_type, data_source, dataset)
        
        # find optimal hyperparameters
        train_start_time = time.time()

        # train the model 
        f = ForecasterFactory.get_forecaster(model_type)
        model = f.train(y_train)

        training_time = time.time() - train_start_time

        # generate the pckl local file 
        #local_path=os.path.expanduser("~/Documents")
        local_path=dm.get_temporary_folder()

        model_file_name = model_name if model_name != None else "Model_" + str(uuid.uuid4()) + ".mdl"
        full_path_to_file =os.path.join(local_path, model_file_name)
        f.save(full_path_to_file)
        
        # upload the pckl file to a blob
        dm.save_model_file(full_path_to_file, model_file_name)

        # evaluate model performance using last test_periods
        test_periods = 4
        y_train2 = y_train[:-test_periods]
        y_true = y_train[-test_periods:]
        f.train(y_train2)
        y_hat = f.forecast(test_periods)["value"]
        mae = f.mae(y_hat, y_true)

        # save model metadata
        model_metadata = {'type': model_type, 'mae': mae, 'aic': model.aic, "model_name" : model_name, "version": f.version(), "model_params":f.model_params,
                           "training_date":datetime.utcnow().strftime("%Y%m%d"), "training_time": training_time }
        dm.save_model_metadata(model_file_name + ".meta", json.dumps(model_metadata))

        # remove local file
        os.remove(full_path_to_file)

        q.put([model_metadata])
        print(f'completed training of {model_type} model')

        return model_metadata

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-e", "--environment", dest="environment",
                    help="one of: [dev,test,prod]", default="dev")

    parser.add_argument("-t", "--datasourcetype", dest="data_source_type",
                    help="the type of data source [test,azure_blob]", default="azure_blob")

    parser.add_argument("-s", "--datasource", dest="data_source",
                    help="for future use---", default="?")

    parser.add_argument("-d", "--dataset", dest="dataset",
                    help="the name of the azure blob", default="test_dataset")

    parser.add_argument("-mt", "--model_type", dest="model_type",
                    help="[arima|ets]", default="ets,arima")

    parser.add_argument("-m", "--model_name", dest="model_name",
                    help="the name of the model", default="test_model")

    return parser.parse_args()


if __name__ == '__main__':
       
    params = parse_arguments()

    print ("Configuration   :", params.environment)
    print ("Data Source Type:", params.data_source_type)
    print ("Data Source.....:", params.data_source)
    print ("Data Set........:", params.dataset)
    print ("Model Type......:", params.model_type)
    print ("Model Name......:", params.model_name)


    fs = Trainer()
    tr = fs.start_training(env = params.environment, data_source_type=params.data_source_type, data_source=params.data_source, 
            dataset=params.dataset, model_type=params.model_type, model_name=params.model_name)

    print(tr)



