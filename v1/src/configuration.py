
class Configuration(object):
    DEBUG = False
    TESTING = False
    storage_account = None
    storage_account_key = None

class ProductionConfig(Configuration):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Configuration):
    DEBUG = True
    storage_account = ""
    storage_account_key = ""
    models_container_name = "models"
    results_container_name = "predictions"
    data_container_name = "customer-data"

class TestingConfig(Configuration):
    TESTING = True


def get_configuration(env):
    switcher = {
        'dev': DevelopmentConfig,
        'test': TestingConfig,
        "prod": ProductionConfig
    }
    module = switcher.get(env, None)
    
    return module() if module != None else None
        
    