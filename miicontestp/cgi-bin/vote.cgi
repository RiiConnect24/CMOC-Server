#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
import MySQLdb
from json import load

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

form = FieldStorage()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()
action = form['action'].value
entryno = form['entryno'].value
craftsno = form['craftsno'].value

cursor.execute('UPDATE mii SET likes = likes+1, permlikes = permlikes+1 WHERE entryno = %s', [entryno])
cursor.execute('UPDATE artisan SET popularity=(SELECT AVG(permlikes) FROM mii WHERE craftsno=%s), votes = votes+1 WHERE craftsno=%s', (craftsno, craftsno)) #add +1 to total votes and set popularity to their average mii permlikes + 10%

cursor.execute('SELECT votes FROM artisan WHERE craftsno = %s', [craftsno])

if int(cursor.fetchone()[0]) >= 1000: #1000 likes needed to become a master artisan
	cursor.execute('UPDATE artisan SET master = 1 WHERE craftsno  = %s', [craftsno])

data = bytes.fromhex('565400000000000000000000000000000000000000000000ffffffffffffffff454e002000000001000000010000000100000001000000010000000100000001')

stdout.buffer.write(b'Content-Type:application/octet-stream\n\n')
stdout.flush()
stdout.buffer.write(data)
stdout.flush()
db.commit()
db.close()
