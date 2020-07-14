import mysql.connector as msc

mydb = msc.connect(
    host='192.168.1.59',
    user='chia',
    passwd='mp5',
)

print(mydb)
