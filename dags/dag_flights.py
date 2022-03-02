
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

#Parameter
year_csv="{{ dag_run.conf['year_csv'] }}"

def read_process_write_file(year_csv):
    
    import json
    import requests
    import pandas as pd
    import numpy as np
    import s3fs
    import sqlalchemy
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import boto3

    df1 = pd.read_csv(year_csv,nrows=2000000)

    print('read success')
    year_file = year_csv.split('/')[-1]
    year_file = year_file.split('.')[0]

    df1 = df1.groupby(['FL_DATE','ORIGIN']).mean()

    df1 = df1[['DEP_DELAY']]

    df1 = df1.reset_index()

    df1 = df1.sort_values('FL_DATE',ascending=True)

    df1.fillna(0,inplace=True)

    p90 = df1['DEP_DELAY'].quantile(0.9)

    df1['pred'] = np.where(df1['DEP_DELAY']>p90,1,0)

    df1['result'] = np.where(df1['DEP_DELAY']>p90,'outlier','normal')

    host="database-1.cqhkk5knhhbz.us-east-1.rds.amazonaws.com"
    port=5432
    dbname=""
    user="postgres"
    password="postgresrds1" 

    database_connection = sqlalchemy.create_engine('postgresql://{0}:{1}@{2}/{3}'.format(user, password,host, dbname)).connect()

    #upload to rds postgres
    df1.to_sql(con=database_connection, name='flights', if_exists='replace',index=False)

    #upload to s3
    df1.to_csv('s3://airline-outliers/dataframes/df{}.csv'.format(year_file), index=False)
    
    df2 = df1.reset_index()

    df2 = df2.sort_values('FL_DATE',ascending=True)

    origin_unique = df2.ORIGIN.unique()

    with PdfPages('foo.pdf') as pdf:
        for i in origin_unique[:]:
            df_temp = df2[df2.ORIGIN==i]
            plt.figure()
            plt.figure()
            plt.title(i)
            plt.xlabel("date")
            plt.ylabel("delay_minutes")
            fig = plt.scatter(df_temp.FL_DATE,df_temp.DEP_DELAY, c=df_temp.pred, ec='k').get_figure()
            pdf.savefig(fig)

    s3 = boto3.resource('s3')
    BUCKET = "airline-outliers"
    s3.Bucket(BUCKET).upload_file("foo.pdf", "plots/plot_{}.pdf".format(year_file))



default_args = {
    'start_date': datetime(year=2022, month=2, day=21)
}

with DAG(
    dag_id='dag_flights',
    default_args=default_args,
    schedule_interval='@yearly',
    description='ETL pipeline for processing users'

) as dag:

    task_flights = PythonOperator(
        task_id='read_process_write_file',
        python_callable=read_process_write_file,
        op_kwargs={"year_csv": year_csv},
    )

    task_flights