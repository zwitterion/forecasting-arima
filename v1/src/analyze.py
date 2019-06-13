import sys

from forecaster.forecaster import Forecaster
from forecaster.datamanager import DataManager

#from forecatser.datamanager import DataManager
#https://docs.python.org/3/library/multiprocessing.html
class Trainer():

    def version(self):
        return Forecaster().version()
        
    def train(self,data_source_type, data_source=None):

        f = Forecaster()
        dm = DataManager()

        y_train = dm.get_data(data_source_type, data_source)
        
        order, seasonal_order = f.grid_search(y_train, max_order=(3,1,1,1,1,1,12), progress=lambda x: print(x))
        model = f.train(y_train, order, seasonal_order)
        print("optimal: {} {}", order, seasonal_order)
        return {'aic': model.aic}


if __name__ == '__main__':
    print ("Arguments:", sys.argv )

    data_source_type = sys.argv[1] if len(sys.argv) > 1 else "test"
    data_source = sys.argv[2] if len(sys.argv) > 2 else None

    print ("Data Source Type:", data_source_type)
    print ("Data Source.....:", data_source)

    fs = Trainer()
    tr = fs.train(data_source_type=data_source_type, data_source=data_source)
    print(tr)