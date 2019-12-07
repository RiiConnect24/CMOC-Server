#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
from struct import pack
import MySQLdb
from json import load

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
		config = load(f)

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

form = FieldStorage()
db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()

craftsno = int(form['craftsno'].value) #receives GET parameter craftsno to insert into the header

cursor.execute('SELECT master,popularity FROM artisan WHERE craftsno = %s', [craftsno])
response = cursor.fetchone()
master = response[0]
popularity = response[1]

cursor.execute('SELECT craftsno FROM artisan ORDER BY votes DESC LIMIT 100')
craftlist = cursor.fetchall()

for n in range(len(craftlist)): #this sucks but idk how to do it in SQL
	if craftsno in craftlist[n]:
		ranking = n
		break
	else:
		ranking = -1 #to counter the +1 below which is needed


data = bytes.fromhex('494E000000000000\
') + u32(craftsno) + bytes.fromhex('\
000000000000000000000000FFFFFFFFFFFFFFFF\
494D005C0000000100000001\
8000003F000000000000000000000000000000000000404086397BCBC2265C280004424031BD28A2088C08401449B88D008A008A25040000000000000000000000000000000000000000EA29\
00000000494E0018000000010000000100000001') + u8(0) + u8(master) + u8(popularity) + u8(0) + u8(ranking + 1) + u8(0) + u8(0) + u8(1) #make a proper f

stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
db.close()