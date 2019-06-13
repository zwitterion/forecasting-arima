"""
For testing purposes only
Usage:
    data_preprocessor csv_in csv_out

"""
import os
import sys
import pandas as pd
from datetime import datetime

csv_in = sys.argv[1]
csv_out = sys.argv[2]

if (not os.path.isfile(csv_in)):
    print("File: {} does not exist.".format(csv_in))
    exit()

if (os.path.isfile(csv_out)):
    print("File: {} already exist. Please delete the local file first.".format(csv_out))
    exit()
    
opt = pd.read_csv(csv_in, sep="|", skiprows=[1])
print(opt.head())
opt["date"] = opt.apply(lambda r: datetime(int(r["Year"]),int(r["Month"]),1), axis=1)
# for some reasons there are opts with dates in the future so we will remove them
opt = opt[opt["date"]<datetime.utcnow()]
opt = opt.set_index("date")

opt.dropna(inplace=True)

opt= opt.groupby("date").sum()["ActualValue"]
opt = opt.resample('MS').mean()
df = opt 

print(df.head())
df.to_csv(csv_out, header=True)

print("File written to: {}".format(csv_out))



