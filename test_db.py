import psycopg2
connection = psycopg2.connect(
    host = 'database-1.cqhkk5knhhbz.us-east-1.rds.amazonaws.com',
    port = 5432,
    user = 'postgres',
    password = 'postgresrds1',
    database=''
    )
cursor=connection.cursor()


sql3 = '''select * from flights limit 100;'''
cursor.execute(sql3)
for i in cursor.fetchall():
	print(i)

connection.commit()
connection.close()
