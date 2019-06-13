from forecaster.arima_forecaster import ArimaForecaster
from forecaster.ets_forecaster import EtsForecaster

class ForecasterFactory(object):

    @staticmethod
    def get_forecaster(forecaster_type):
        models = {"arima": ArimaForecaster,
                  "ets": EtsForecaster}
        return models.get(forecaster_type)()

    @staticmethod
    def load_model(full_path_to_file):
        """
        Loads a model from a given file
        We need to inspect the given file ot fecth metdata to avoid the try/except. This is not ideal but the overhead is minimum.

        Arguments:
            full_path_to_file {[string]} -- full path to model file
        
        Returns:
            [Forecaster] -- An instance of ArimaForecaster or EtsForecaster
        """

        f = None
        try:
            # assume it is ETS - if not try Arima
            f = EtsForecaster.load(full_path_to_file)
        except: #Exception as ex:
            pass

        if f == None:
            try:
                f = ArimaForecaster.load(full_path_to_file)
            except:
                pass

        return f