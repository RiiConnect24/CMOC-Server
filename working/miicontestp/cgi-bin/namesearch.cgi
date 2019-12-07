#!/usr/local/bin/python3.7
import MySQLdb
from cmoc import Search
from sys import stdout
from cgi import FieldStorage
from json import load

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

form = FieldStorage()
Search = Search()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
entryno = int(form['entryno'].value)
cursor = db.cursor()
cursor.execute('SELECT craftsno, nickname FROM mii WHERE entryno = %s', [entryno])
result = cursor.fetchone()
craftsno = int(result[0])
nickname = str(result[1])

cursor.execute('SELECT craftsno,entryno FROM mii WHERE nickname LIKE %s', [('%' + nickname + '%')])
numbers = cursor.fetchall()

miilist = []

for i in range(len(numbers)): #add the artisan data to each mii based on their craftsno
	cursor.execute('SELECT entryno,initial,permlikes,skill,country,miidata FROM mii WHERE craftsno = %s AND entryno = %s', (numbers[i][0], numbers[i][1]))
	mii = cursor.fetchone()
	cursor.execute('SELECT miidata,craftsno,master FROM artisan WHERE craftsno = %s', [numbers[i][0]])
	artisan = cursor.fetchone()
	miilist.append(mii + artisan)

processed = Search.build('NS', miilist, entryno, craftsno)

mii = b''
for i in range(0, len(processed)):
	mii += (processed[i])

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(mii)
stdout.flush()

db.close()
