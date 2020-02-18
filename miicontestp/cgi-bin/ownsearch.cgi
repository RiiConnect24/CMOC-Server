#!/usr/bin/env python
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

import MySQLdb
from cmoc import OwnSearch
from sys import stdout
from cgi import FieldStorage
from json import load

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

form = FieldStorage()
OwnSearch = OwnSearch()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
craftsno = int(form['craftsno'].value)
cursor = db.cursor()

cursor.execute('(SELECT entryno,initial,permlikes,skill,country,miidata FROM mii WHERE craftsno = %s ORDER BY entryno DESC LIMIT 5) UNION (SELECT entryno,initial,permlikes,skill,country,miidata FROM mii WHERE craftsno = %s ORDER BY RAND() LIMIT 50)', (craftsno, craftsno)) #gets all the artisan's miis
miis = cursor.fetchall()[:50] #the list must be trimmed to 50 because mysql removes duplicate rows when using UNION, and would normally show 45 to 50 miis

processed = OwnSearch.build(miis, craftsno)
mii = b''

for i in range(0, len(processed)):
	mii += (processed[i])

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(mii)

stdout.flush()

db.close()
