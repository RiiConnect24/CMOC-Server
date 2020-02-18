#!/usr/bin/env python
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

import MySQLdb
from cmoc import Search
from sys import stdout
from cgi import FieldStorage
from json import load
import struct

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)
        
def u32(data):
	if not 0 <= data <= 4294967295:
		log("u32 out of range: %s" % data, "INFO")
		data = 0
	return struct.pack(">I", data)

form = FieldStorage()
Search = Search()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
entryno = int(form['entryno'].value)
cursor = db.cursor()

cursor.execute('SELECT COUNT(*) FROM mii WHERE entryno = %s', [entryno])

if cursor.fetchone()[0] == 0: #no result for provided entryno, probably a cached mii
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(bytes.fromhex('4E53000000000000') + u32(entryno) + bytes.fromhex('000000000000000000000000FFFFFFFFFFFFFFFF'))
	stdout.flush()
	exit()

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
