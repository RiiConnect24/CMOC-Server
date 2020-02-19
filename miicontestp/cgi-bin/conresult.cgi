#!/usr/bin/env python
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

from cgi import FieldStorage
from sys import stdout
from cmoc import ConResult
import MySQLdb
from json import load
from sys import stdout

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
        config = load(f)

def result(id):
	stdout.flush()
	stdout.buffer.write(b'X-RESULT: ' + str(id).encode() + b'\n\n')
	stdout.flush()
	exit()

db = MySQLdb.connect('sponge.press', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()
cr = ConResult()
form = FieldStorage()
contestno = form['contestno'].value

artisans = []
try: #bangladesh code but it works
	artisans.append(form['craftsno1'].value)
	artisans.append(form['craftsno2'].value)
	artisans.append(form['craftsno3'].value)
	judgingMiis = True

except KeyError:
	artisans.append(form['craftsno1'].value)
	judgingMiis = False

if judgingMiis == True: 
	try:
		artisans.append(form['craftsno4'].value)

	except KeyError:
		pass

miilist = []
for i in artisans:
	cursor.execute('SELECT `rank` FROM conmiis WHERE craftsno = %s AND contest = %s', (i, contestno))
	rank = cursor.fetchone()[0]
	try:
		miilist.append((int(i), int(rank)))
	except:
		error = (str(i) + ' ' + str(rank) + ' ' + str(contestno))

data = cr.build(int(contestno), miilist)
stdout.buffer.write(b'Content-Type:application/octet-stream\n\n')
stdout.flush()
stdout.buffer.write(data)
stdout.flush()

db.close()