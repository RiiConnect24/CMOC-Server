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

if cursor.fetchone()[0] == 0: #no result for provided entryno
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(bytes.fromhex('5352000000000000') + u32(entryno) + bytes.fromhex('000000000000000000000000FFFFFFFFFFFFFFFF'))
	stdout.flush()
	exit()

cursor.execute('SELECT craftsno FROM mii WHERE entryno = %s', [entryno])
craftsno = int(cursor.fetchone()[0])
cursor.execute('SELECT entryno,initial,permlikes,skill,country,miidata FROM mii WHERE entryno = %s', [entryno]) #gets all the artisan's miis
mii = cursor.fetchall()
cursor.execute('SELECT miidata,master FROM artisan WHERE craftsno = %s', [craftsno]) #gets the artisan's data and master flag
response = cursor.fetchone()
artisan = response[0]
master = response[1]

miis = []
for i in range(len(mii)):
	miis.append(mii[i] + (artisan, craftsno, master)) #adds the artisan data into the array of mii data

processed = Search.build('SR', miis, entryno, craftsno)
mii = b''

for i in range(0, len(processed)):
	mii += (processed[i])

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(mii)
stdout.flush()

db.close()
