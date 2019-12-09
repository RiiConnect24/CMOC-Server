#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
from struct import pack
from base64 import b64encode
import MySQLdb
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

nickname = form['nickname'].value
country = form['country'].value
cngroup = form['cngroup'].value
wiino = form['wiino'].value
miidata = b64encode(form['miidata'].file.read().encode('utf-8', 'surrogateescape')).decode() #hack to base64 encode multipart form embedded binary

craftsno = form['craftsno'].value
cursor.execute("SELECT count(*) FROM artisan WHERE craftsno = %s AND wiino = %s", (craftsno, wiino))

if cursor.fetchone()[0] != 0: #UPDATE a mii entry if it already exists, and give it the same entry number
	cursor.execute("UPDATE artisan SET nickname = %s, miidata = %s WHERE craftsno = %s", (nickname, miidata, craftsno))
	result = int(craftsno)

else:
	cursor.execute("INSERT INTO artisan(nickname, postcount, popularity, votes, master, country, cn_group, wiino, miidata)\
	VALUES(%s, 0, 13, 0, 0, %s, %s, %s, %s)", (nickname, country, cngroup, wiino, miidata)) 
	cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'cmoc' AND TABLE_NAME = 'artisan'") #get next craftsno in list
	result = int(cursor.fetchone()[0]) -1 #gives the user a new index BUT REMOVE ONE OR ELSE!!!!! YOU MUST!!!!!!!!!!!
	statsd.increment("cmoc.registers")

data = bytes.fromhex('4D5300000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF454E000C00000001') + u32(int(result)) #tells CMOC its craftsno

stdout.flush()
stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
db.commit()
db.close()
