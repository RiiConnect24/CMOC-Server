#!/usr/local/bin/python3.7
import MySQLdb
from cmoc import OwnSearch
from sys import stdout
from cgi import FieldStorage
from json import load
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

form = FieldStorage()
OwnSearch = OwnSearch()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
craftsno = int(form['craftsno'].value)
cursor = db.cursor()

cursor.execute('SELECT entryno,initial,permlikes,skill,country,miidata FROM mii WHERE craftsno = %s ORDER BY RAND() LIMIT 50', [craftsno]) #gets all the artisan's miis
miis = cursor.fetchall()

processed = OwnSearch.build(miis, craftsno)
mii = b''

for i in range(0, len(processed)):
	mii += (processed[i])

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(mii)
with open ('/var/www/wapp.wii.com/miicontest/public_html/150/ownsearch.dec', 'wb') as file:
	file.write(mii)

stdout.flush()

db.close()
