#!/usr/bin/env python
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

from cgi import FieldStorage
from html import escape
from os import environ
from sys import stdout
import MySQLdb
from json import load

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
        config = load(f)

def verifyMac(mac): #verify macaddress is valid and from a Wii
	oui = ['0009BF', '001656', '0017AB', '00191D', '0019FD', '001AE9', '001B7A', '001BEA', '001CBE', '001DBC', '001E35', '001EA9', '001F32', '001FC5', '002147', '0021BD', '00224C', '0022AA', '0022D7', '002331', '0023CC', '00241E', '002444', '0024F3', '0025A0', '002659', '002709', '0403D6', '182A7B', '2C10C1', '34AF2C', '40D28A', '40F407', '582F40', '58BDA3', '5C521E', '606BFF', '64B5C6', '78A2A0', '7CBB8A', '8C56C5', '8CCDE8', '9458CB', '98B6E9', '9CE635', 'A438CC', 'A45C27', 'A4C0E1', 'B87826', 'B88AEC', 'B8AE6E', 'CC9E00', 'CCFB65', 'D86BF7', 'DC68EB', 'E00C7F', 'E0E751', 'E84ECE', 'ECC40D']
	if len(mac) == 12 and mac.upper()[:6] in oui: return True
	else: return False

def return403():
	stdout.flush()
	stdout.buffer.write(b'Status: 403 Forbidden\n\n')
	stdout.flush()
	exit()

def result(id):
	stdout.flush()
	stdout.buffer.write(b'X-RESULT: ' + str(id).encode() + b'\n\n')
	stdout.flush()
	exit()

def returnFail():
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(bytes.fromhex('435600000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF'))
	stdout.flush()

def returnPass():
	stdout.buffer.write(b'Content-Type:application/octet-stream\n\n')
	stdout.flush()
	stdout.buffer.write(bytes.fromhex('435600000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF4E4C001000000001FFFFFFFFFFFFFFFF'))
	stdout.flush()

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()

form = FieldStorage()
contestno = form['contestno'].value
macadr = form['macadr'].value
ip = escape(environ["REMOTE_ADDR"])

try:
	craftsno = form['craftsno1'].value.split(',') #up to 3 voted craftsnos are stored into an array

except KeyError:  #don't do anything because the user just voted on the same miis as last time
	returnPass()
	exit()

firstVote = True

if verifyMac(macadr) == False:	result(701)

if len(craftsno) > 3: #dumbass
	return403()

cursor.execute('SELECT status FROM contests WHERE id = %s', [contestno])
if cursor.fetchone()[0] != 'judging': #prevent voting on a contest not accepting votes
	returnFail()
	exit()

cursor.execute('SELECT COUNT(*) FROM artisan WHERE mac = %s', [macadr])
if cursor.fetchone()[0] == 0:	result(704) #no artisan with this registered mac address

cursor.execute('SELECT COUNT(*) FROM convotes WHERE mac = %s AND id = %s', (macadr, contestno))
if cursor.fetchone()[0] != 0: firstVote = False

cursor.execute('SELECT ip FROM convotes WHERE mac = %s AND id = %s', (macadr, contestno))
ipResult = cursor.fetchone()

if ipResult != None:
	if ipResult[0] != ip:	result(706) #user is probably spoofing their mac address, or has a dynamic ip

if firstVote:
	try:
		cursor.execute('INSERT INTO convotes (id, craftsno1, craftsno2, craftsno3, mac, ip) VALUES (%s, %s, %s, %s, %s, %s)', (contestno, craftsno[0], craftsno[1], craftsno[2], macadr, ip)) #log their vote
	except IndexError:
		log = str(form['craftsno1'].value)

		raise IndexError(log)

else: #the user is changing their vote
	cursor.execute('SELECT craftsno1, craftsno2, craftsno3 FROM convotes WHERE mac = %s AND id = %s LIMIT 1', (macadr, contestno))
	result = cursor.fetchone()
	newVotes = []
	for c in range(3): #horrible
		try:
			newVotes.append(craftsno[c])

		except IndexError:
			newVotes.append(result[c])

	cursor.execute('UPDATE convotes SET craftsno1 = %s, craftsno2 = %s, craftsno3 = %s WHERE mac = %s AND id = %s', (newVotes[0], newVotes[1], newVotes[2], macadr, contestno))

db.commit()
db.close()

returnPass()