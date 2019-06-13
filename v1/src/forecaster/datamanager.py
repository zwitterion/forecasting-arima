import os
import uuid
import pandas as pd
import datetime
import dateutil.parser

# for test data set
import statsmodels.api as sm

from azure.storage.blob import BlockBlobService

class DataManager():
    def __init__(self, config):
        self.config = config
        

        
    def get_data(self, data_source_type, data_source, dataset, full_path_to_file=None, container=None):
        

        if (full_path_to_file == None):
            #local_path=os.path.expanduser("~/Documents")
            local_path=self.get_temporary_folder()
            local_file_name ="dataset_" + str(uuid.uuid4()) + ".csv"
            full_path_to_file =os.path.join(local_path, local_file_name)

        if (data_source_type == "test"):
            df = self.get_test_data()
            df.columns = ["date"]
            df.to_csv(full_path_to_file, header=True)

        if (data_source_type== "azure_blob"):
            container_name = container if container != None else self.config.data_container_name
            block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
            block_blob_service.get_blob_to_path(container_name, dataset, full_path_to_file)
            # assume [date, value] columns
            df = pd.read_csv(full_path_to_file)
            df["date"] = df["date"].apply(lambda x: dateutil.parser.parse(x))
            df = df.set_index("date")
            df = df.resample("MS").mean()
        
        return df

    def save_data(self, source_type, source, full_path_to_file, local_file_name):
        """
        Only used for testing. The consumer of the API
        is responsible for storing/preparing the data that will be retrieved 
        using get_data()
        """
        assert(self.config.storage_account)
        assert(self.config.storage_account_key)
        assert(self.config.data_container_name)
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        block_blob_service.create_container(self.config.data_container_name, fail_on_exist=False, public_access=None) 
        block_blob_service.create_blob_from_path(self.config.data_container_name , local_file_name, full_path_to_file)

        return None

    def get_test_data(self):
        co2 = pd.DataFrame(sm.datasets.co2.load().data)
        co2["date"] = co2["date"].apply(lambda b: datetime.datetime(int(b[0:4]),int(b[4:6]),int(b[6:])))
        co2 = co2.set_index('date')
        co2 = co2.resample('MS').mean()
        co2 = co2.fillna(co2.bfill())
        return co2["co2"]

    def save_model_file(self, full_path_to_file, local_file_name):
        """Uploads a local file containg a model to the blob container specifed by self.config.models_container_name
            If the container name does not exists it will be created.
        Arguments:
            full_path_to_file {[type]} -- full path to t the local file
            local_file_name {[type]} -- the file name.
        """

        assert(self.config.storage_account)
        assert(self.config.storage_account_key)
        assert(self.config.models_container_name)
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        block_blob_service.create_container(self.config.models_container_name, fail_on_exist=False, public_access=None) 
        block_blob_service.create_blob_from_path(self.config.models_container_name , local_file_name, full_path_to_file)

    def get_model_file(self, full_path_to_file, blob_name):  #TODO!!!!!!!!!!!!!!!!!!
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        block_blob_service.get_blob_to_path(self.config.models_container_name, blob_name, full_path_to_file)

    def save_result(self, blob_name, text_data):
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        block_blob_service.create_container(self.config.results_container_name, fail_on_exist=False, public_access=None) 
        if block_blob_service.exists(self.config.results_container_name, blob_name):
            block_blob_service.delete_blob(self.config.results_container_name, blob_name)

        block_blob_service.create_blob_from_text(self.config.results_container_name, blob_name, text_data)
        return
        
    def save_model_metadata(self, blob_name, text_data):
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        block_blob_service.create_container(self.config.models_container_name, fail_on_exist=False, public_access=None) 
        if block_blob_service.exists(self.config.models_container_name, blob_name):
            block_blob_service.delete_blob(self.config.models_container_name, blob_name)

        block_blob_service.create_blob_from_text(self.config.models_container_name, blob_name, text_data)
        return

    def activate_model(self, model_name, active_model_name):
        block_blob_service = BlockBlobService(account_name=self.config.storage_account , account_key=self.config.storage_account_key) 
        # copy model 
        blob_url = block_blob_service.make_blob_url(self.config.models_container_name, model_name)
        block_blob_service.copy_blob(self.config.models_container_name, active_model_name, blob_url)
        # copy model metadata
        blob_url = block_blob_service.make_blob_url(self.config.models_container_name, model_name + ".meta")
        block_blob_service.copy_blob(self.config.models_container_name, active_model_name + ".meta", blob_url)

    def get_temporary_folder(self):
        """returns a path to a folder where temp files can be stored.
        
        Returns:
            [string] -- path to local folder to store temp file
        """

        local_path=os.path.realpath("./data")
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        return local_path

if __name__ == '__main__':
    dm = DataManager(None)
    df = dm.get_data("test", None, None)
    print(df.head())