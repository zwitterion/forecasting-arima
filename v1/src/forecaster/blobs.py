
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

import json
import hashlib


class Blob(object):
    config = None
    block_blob_service = None

    def __init__(self, config):
        self.config = config
        self.block_blob_service = BlockBlobService(account_name=config.storage_account, account_key=config.storage_account_key) 
        if (self.block_blob_service.exists(config.models_container_name) == False):
            self.block_blob_service.create_container(config.models_container_name, fail_on_exist=False)

        return

    def get_id(self, text):
        hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return hash

    def get(self, id):
        document = None
        try:
            blob = self.block_blob_service.get_blob_to_text(self.config.text_container_name, id)
            text = blob.content
            document = json.loads(text)
            # print("Fetched blob:" + text)
        
        except BaseException as e:
            print('Failed to fetch blob: '+ str(e))
            return None
        
        return document

    def put(self, id, document):
        self.block_blob_service.create_blob_from_text(
            self.config.text_container_name, 
            id, 
            json.dumps(document),
            content_settings=ContentSettings(content_type='application/json')
        )


if __name__ == '__main__':
    config = Config("dev")
    b = Blob(config)
    hash = b.get_id("http://foo.com")
    print(hash)     


    