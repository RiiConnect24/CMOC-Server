#!/usr/bin/env python
from sys import stdout
from cgi import FieldStorage
from struct import pack
import MySQLdb
from json import load
from cmoc import QuickList
import sentry_sdk

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
		config = load(f)

sentry_sdk.init(config["sentry_url"])

def u8(data):
	if not 0 <= data <= 255:
		log("u8 out of range: %s" % data, "INFO")
		data = 0
	return pack(">B", data)

def u32(data):
	if not 0 <= data <= 4294967295:
		log("u32 out of range: %s" % data, "INFO")
		data = 0
	return pack(">I", data)

ql = QuickList()
form = FieldStorage()
db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()

craftsno = int(form['craftsno'].value) #receives GET parameter craftsno to insert into the header

#must be sent craftsno, entryno, most popular mii, initials, master artisan flag, popularity and ranking

cursor.execute('SELECT master,popularity FROM artisan WHERE craftsno = %s', [craftsno])
response = cursor.fetchone()

if response == None: #sends user save file corrupted message
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(bytes.fromhex('494E000000000000') + u32(int(craftsno)) + bytes.fromhex('000000000000000000000000FFFFFFFF00000000'))
	exit()

master = response[0]
popularity = response[1]

cursor.execute('SELECT craftsno FROM artisan WHERE craftsno !=100000993 ORDER BY votes DESC LIMIT 100')
craftlist = cursor.fetchall()

for n in range(len(craftlist)): #this sucks but idk how to do it in SQL
	if craftsno in craftlist[n]:
		ranking = n
		break
	else:
		ranking = 0

cursor.execute('SELECT entryno,miidata,initial FROM mii WHERE craftsno = %s ORDER BY permlikes DESC LIMIT 1', [craftsno])
response = cursor.fetchone()

if response == None: #displays the default mii if the user has 0 posts
	entryno = 1
	miidata = 'XYAAAD8AAQD9EUBAhjl7y8ImXCgABEJAMb0oogiMCEAUSbiNAIoAiiUEMQBQAAAA6ik='
	initial = '00'
	
else:
	entryno = response[0]
	miidata = response[1]
	initial = response[2]

data = ql.infoBuild(craftsno, entryno, miidata, initial, master, popularity, ranking)

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
db.close()
