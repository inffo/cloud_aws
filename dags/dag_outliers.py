
import json
import requests
import pandas as pd
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def read_process_write_file():

    files = ['s3://airline-outliers/2009.csv','s3://airline-outliers/2010.csv','s3://airline-outliers/2011.csv','s3://airline-outliers/2012.csv','s3://airline-outliers/2013.csv','s3://airline-outliers/2014.csv','s3://airline-outliers/2015.csv','s3://airline-outliers/2016.csv','s3://airline-outliers/2017.csv','s3://airline-outliers/2018.csv']

    for file_name in files:
            
        df1 = pd.read_csv(file_name,nrows=100)

        print('read success')
        year_file = file_name.split('/')[-1]
        year_file = year_file.split('.')[0]
        
        df1 = df1.groupby(['FL_DATE','ORIGIN']).mean()

        df1 = df1[['DEP_DELAY']]

        df1 = df1.reset_index()

        df1 = df1.sort_values('FL_DATE',ascending=True)
        # check fillna , filling with 0 means that it has no delay. What does na means? that it never departured?
        df1.fillna(0,inplace=True)

        p90 = df1['DEP_DELAY'].quantile(0.9)

        df1['pred'] = np.where(df1['DEP_DELAY']>p90,1,0)

        df1['result'] = np.where(df1['DEP_DELAY']>p90,'outlier','normal')

        host="database-1.cqhkk5knhhbz.us-east-1.rds.amazonaws.com"
        port=5432
        dbname=""
        user="postgres"
        password="postgresrds1" #now they make you add numbers...

        database_connection = sqlalchemy.create_engine('postgresql://{0}:{1}@{2}/{3}'.format(user, password,host, dbname)).connect()

        df1.to_sql(con=database_connection, name='flights', if_exists='replace',index=False)

        df2 = df1.reset_index()

        df2 = df2.sort_values('FL_DATE',ascending=True)

        origin_unique = df2.ORIGIN.unique()

        with PdfPages('foo.pdf') as pdf:
            for i in origin_unique[:2]:
                df_temp = df2[df2.ORIGIN==i]
                plt.figure()
                fig = plt.scatter(df_temp.FL_DATE,df_temp.DEP_DELAY, c=df_temp.pred, ec='k').get_figure()
                pdf.savefig(fig)

        s3 = boto3.resource('s3')
        BUCKET = "airline-outliers"
        s3.Bucket(BUCKET).upload_file("foo.pdf", "plots/plot_{}.pdf".format(year_file))



default_args = {
    'start_date': datetime(year=2022, month=2, day=21)
}

with DAG(
    dag_id='dag_outliers2',
    default_args=default_args,
    schedule_interval='@daily',
    description='ETL pipeline for processing users'
) as dag:


    import os
    import pandas as pd
    #from sklearn.ensemble import IsolationForest
    import numpy as np
    #import matplotlib.pyplot as plt
    #import matplotlib.colors as mcolors
    import s3fs
    import os
    import sqlalchemy

    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import boto3
    # Task 1 - Fetch user data from the API
    task_extract_users = PythonOperator(
        task_id='read_process_write_file',
        python_callable=read_process_write_file,
        #op_kwargs={'url': 'https://jsonplaceholder.typicode.com/users'}
    )

    task_extract_users