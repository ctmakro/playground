import psycopg2 as pg

conn = pg.connect(host='192.168.1.59',user='postgres',password='')

conn.autocommit = True

cur = conn.cursor()
cur.execute('create database test')

# print(cur.fetchall())
