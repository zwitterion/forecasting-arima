
# train a model to forecast co2 levels using ARIMA
python .\train.py -t azure_blob -d co2.csv -mt arima -m co2_model 
python .\train.py -t azure_blob -d co2.csv -mt ets -m co2_etsmodel 

# predict
python .\predict.py -m co2_model  -p 12

# graph
python .\graph.py -d co2.csv -p co2_model-prediction.csv


# contonso
python .\train.py -t azure_blob -d contoso.csv -m contoso -mt ets 
python .\predict.py -m contoso -p 12
python .\graph.py -d contoso.csv -p contoso-prediction.csv


python .\src/train.py -t azure_blob -d contoso.csv -m etscontoso -mt ets
python .\src/predict.py -m etscontoso -p 12
python .\src/graph.py -d contoso.csv -p etscontoso-prediction.csv
