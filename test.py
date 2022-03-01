import s3fs
import pandas as pd

df1 = pd.read_csv('s3://airline-outliers/2009.csv')
