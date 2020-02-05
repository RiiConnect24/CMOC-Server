#!/usr/local/bin/python3.7
from sys import stdout
from cgi import FieldStorage
from base64 import b64encode, b64decode
import MySQLdb
from struct import pack
from json import load
from datadog import statsd
import sentry_sdk
sentry_sdk.init("https://d3e72292cdba41b8ac005d6ca9f607b1@sentry.io/1860434")

with open("/var/rc24/File-Maker/Tools/CMOC/config.json", "r") as f:
        config = load(f)

def u32(data):
    if not 0 <= data <= 4294967295:
        log("u32 out of range: %s" % data, "INFO")
        data = 0
    return pack(">I", data)

def return403():
	stdout.flush()
	stdout.buffer.write(b'Status: 403 Forbidden\n\n')
	stdout.flush()
	exit()

def verifyMac(mac): #verify macaddress is valid and from a Wii
	oui = ['0009BF', '001656', '0017AB', '00191D', '0019FD', '001AE9', '001B7A', '001BEA', '001CBE', '001DBC', '001E35', '001EA9', '001F32', '001FC5', '002147', '0021BD', '00224C', '0022AA', '0022D7', '002331', '0023CC', '00241E', '002444', '0024F3', '0025A0', '002659', '002709', '0403D6', '182A7B', '2C10C1', '34AF2C', '40D28A', '40F407', '582F40', '58BDA3', '5C521E', '606BFF', '64B5C6', '78A2A0', '7CBB8A', '8C56C5', '8CCDE8', '9458CB', '98B6E9', '9CE635', 'A438CC', 'A45C27', 'A4C0E1', 'B87826', 'B88AEC', 'B8AE6E', 'CC9E00', 'CCFB65', 'D86BF7', 'DC68EB', 'E00C7F', 'E0E751', 'E84ECE', 'ECC40D']
	if len(mac) == 12 and mac.upper()[:6] in oui: return True
	else: return False

form = FieldStorage(errors = 'surrogateescape') #surrogateescape is used to get binary data in forms that are mixed with string data

db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', charset='utf8mb4')
cursor = db.cursor()
entryno = form['entryno'].value
wiino = form['wiino'].value
macadr = form['macadr'].value
country = form['country'].value
cngroup = form['cngroup'].value
sex = form['sex'].value
skill = form['skill'].value
nickname = form['nickname'].value
miiid = form['miiid'].value
craftsno = form['craftsno'].value
initial = form['initial'].value
miidata = b64encode(form['miidata'].file.read().encode('utf-8', 'surrogateescape')).decode() #hack to base64 encode multipart form embedded binary

#mii data length in base64 should ALWAYS be exactly 104 bytes
if len(miidata) != 104 or len(form['nickname'].value) > 10 or len(form['nickname'].value) < 1:
	return403()

cursor.execute("SELECT wiino FROM artisan WHERE craftsno = %s", [craftsno])
wiinoResult = cursor.fetchone()

if wiinoResult == None:
	return403()

if verifyMac(macadr) == False:
	return403()

if int(wiinoResult[0]) == int(wiino): #prevents uploading if its wii number isnt the same as the artisan's
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
		cursor.execute("UPDATE artisan SET lastpost = (SELECT CURRENT_TIMESTAMP()) WHERE craftsno = %s", [craftsno])
		statsd.increment("cmoc.posts")

	cursor.execute("SELECT mac FROM artisan WHERE craftsno = %s", [craftsno]) #log their mac address since its needed now for contests
	if cursor.fetchone()[0] == None:
		cursor.execute("UPDATE artisan SET mac = %s WHERE craftsno = %s", (macadr, craftsno))

	data = bytes.fromhex('505300000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF454E000C00000001') + u32(result) #responds with the mii's entry number
	stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
	stdout.flush()
	stdout.buffer.write(data)
	stdout.flush()

	db.commit()
	db.close()

else: #403 them if they're on a different wii than the one they registered their artisan with
	return403()
