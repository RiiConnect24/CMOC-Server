#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
from base64 import b64encode, b64decode
import MySQLdb
from struct import pack
from cmoc import AddMii, ResetList
from os import stat
from json import load
from datadog import statsd

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

def u32(data):
    if not 0 <= data <= 4294967295:
        log("u32 out of range: %s" % data, "INFO")
        data = 0
    return pack(">I", data)

form = FieldStorage(errors = 'surrogateescape') #surrogateescape is used to get binary data in forms that are mixed with string data

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()
entryno = form['entryno'].value
wiino = form['wiino'].value
country = form['country'].value
cngroup = form['cngroup'].value
sex = form['sex'].value
skill = form['skill'].value
nickname = form['nickname'].value
miiid = form['miiid'].value
craftsno = form['craftsno'].value
initial = form['initial'].value
miidata = b64encode(form['miidata'].file.read().encode('utf-8', 'surrogateescape')).decode() #hack to base64 encode multipart form embedded binary

cursor.execute("SELECT wiino FROM artisan WHERE craftsno = %s", [craftsno])
if int(cursor.fetchone()[0]) == int(wiino): #prevents uploading if its wii number isnt the same as the artisan's
	cursor.execute("SELECT count(*) FROM mii WHERE craftsno = %s AND miiid = %s", (craftsno, miiid))

	if cursor.fetchone()[0] != 0: #UPDATE a mii entry if it already exists, and give it the same entry number
		cursor.execute("UPDATE mii \
		SET craftsno = %s, initial = %s, likes = 0, permlikes = 18, skill = %s, nickname = %s, sex = %s, country = %s, cngroup = %s, wiino = %s, miiid = %s, miidata = %s\
		WHERE craftsno = %s AND miiid = %s", (craftsno, initial, skill, nickname, sex, country, cngroup, wiino, miiid, miidata, craftsno, miiid))
		result = int(entryno)

	else:
		cursor.execute("INSERT INTO mii (craftsno, initial, likes, permlikes, skill, nickname, sex, country, cngroup, wiino, miiid, miidata) \
		VALUES(%s, %s, 0, 18, %s, %s, %s, %s, %s, %s, %s, %s)", (craftsno, initial, skill, nickname, sex, country, cngroup, wiino, miiid, miidata)) #add mii to table. 0 is set because ID auto-increments
		cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'cmoc' AND TABLE_NAME = 'mii'") #get next entryno in list
		result = int(cursor.fetchone()[0]) - 1 #gives the user this mii's index, rather than the one ahead of it
		cursor.execute("UPDATE artisan SET postcount = postcount+1 WHERE craftsno = %s", [craftsno])
		statsd.increment("cmoc.posts")

	data = bytes.fromhex('505300000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF454E000C00000001') + u32(result) #responds with the mii's entry number
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(data)
	stdout.flush()

	db.commit()
	db.close()

else: #403 them if they're on a different wii than the one they registered their artisan with
	stdout.flush()
	stdout.buffer.write(b'Status: 403 Forbidden\n\n')
	stdout.flush()
