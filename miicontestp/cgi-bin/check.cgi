#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
import MySQLdb
from struct import pack
from json import load
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

def u32(data):
    if not 0 <= data <= 4294967295:
        log("u32 out of range: %s" % data, "INFO")
        data = 0
    return pack(">I", data)

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)


form = FieldStorage()
db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()
craftsno = form['craftsno'].value
miiid = form['miiid'].value

cursor.execute("SELECT count(*) FROM mii WHERE craftsno = %s AND miiid = %s", (craftsno, miiid))

if cursor.fetchone()[0] != 0:
	cursor.execute("SELECT entryno FROM mii WHERE craftsno = %s AND miiid = %s", (craftsno, miiid))
	result = cursor.fetchone()[0]

else:
	result = 0

data = bytes.fromhex('434800000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF454E000C00000001') + u32(result)
stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
db.close()
