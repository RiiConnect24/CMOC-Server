#!/usr/bin/env python
import cgi, cgitb
#cgitb.enable()
import MySQLdb
import lz4.block
from base64 import b64decode
from os.path import exists
from subprocess import call, DEVNULL
from json import load
from cmoc import wii2studio

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
        config = load(f)

def decodeMii(data): #takes compressed and b64 encoded data, returns binary mii data
	return(lz4.block.decompress(b64decode(data.encode()), uncompressed_size = 76))

def decToEntry(num: int) -> str: #takes decimal int, outputs 12 digit entry number string
	num ^= ((num << 0x1E) ^ (num << 0x12) ^ (num << 0x18)) & 0xFFFFFFFF
	num ^= (num & 0xF0F0F0F) << 4
	num ^= (num >> 0x1D) ^ (num >> 0x11) ^ (num >> 0x17) ^ 0x20070419

	crc = (num >> 8) ^ (num >> 24) ^ (num >> 16) ^ (num & 0xFF) ^ 0xFF
	if 232 < (0xd4a50fff < num) + (crc & 0xFF):
		crc &= 0x7F

	crc &= 0xFF
	return str(int((format(crc, '08b') + format(num, '032b')), 2)).zfill(12)

def entryToDec(num: str) -> int: #takes 12 digit entry number string, outputs decimal int
	num = int(format(int(num), '032b').zfill(40)[8:], 2)
	num ^= 0x20070419
	num ^= (num >> 0x1D) ^ (num >> 0x11) ^ (num >> 0x17)
	num ^= (num & 0xF0F0F0F) << 4
	num ^= ((num << 0x1E) ^ (num << 0x12) ^ (num << 0x18)) & 0xFFFFFFFF

	return num

print('Content-type:text/html\r\n\r\n')

head = '<!DOCTYPE html>\n<html>\n<head>\n<title>Mii Search</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">\n<link href="https://miicontest.wii.rc24.xyz/css/style.css" rel="Stylesheet" type="text/css" />\n<link href="https://miicontest.wii.rc24.xyz/css/ctmkf.css" rel="Stylesheet" type="text/css" />\n<link rel="apple-touch-icon" sizes="180x180" href="https://miicontest.wii.rc24.xyz/apple-touch-icon.png">\n<link rel="icon" type="image/png" sizes="32x32" href="https://miicontest.wii.rc24.xyz/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="16x16" href="https://miicontest.wii.rc24.xyz/favicon-16x16.png">\n<link rel="manifest" href="https://miicontest.wii.rc24.xyz/site.webmanifest">\n<link rel="mask-icon" href="https://miicontest.wii.rc24.xyz/safari-pinned-tab.svg" color="#89c0ca">\n<meta name="msapplication-TileColor" content="#2d89ef">\n<meta name="theme-color" content="#ffffff">\n</head>\n\n<body class="center">\n<h2><img width=60 src="https://miicontest.wii.rc24.xyz/search/search.png"> Mii Search by Entry Number</h2>'
form = cgi.FieldStorage()
query = form.getvalue('query')
db = MySQLdb.connect('localhost', config['dbuser'], config['dbpass'], 'cmoc', use_unicode=True, charset='utf8mb4')
cursor = db.cursor()

validEntryno = False
validQuery = ''
if len(query) < 15:
	for c in query:
		if c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
			validQuery += c

	if len(validQuery) == 12:
		validEntryno = True
		query = validQuery

if not validEntryno:
	print(head)
	print('Invalid Entry Number.')
	exit()

headers = ['Mii', 'Nickname', 'Entry Number', 'Initials', 'Likes', 'Creator']
for h in range(len(headers)):
	headers[h] = '\t\t<th>' + headers[h] + '</th>\n'
headers = '\t<tr>\n' + ''.join(headers) + '</tr>\n'

entryno = entryToDec(query)
cursor.execute('SELECT mii.miidata, mii.entryno, mii.initial, mii.permlikes, mii.nickname, artisan.nickname, artisan.master, mii.craftsno FROM mii, artisan WHERE entryno = %s AND artisan.craftsno = mii.craftsno', [entryno])
row = cursor.fetchall()

table = '<p>Click on a Mii to download it.</p>\n<table class="striped" align="center">\n' + headers
for i in range(len(row)):
	artisan = row[i][5]
	initial = row[i][2]
	mii_filename = '/var/www/wapp.wii.com/miicontest/public_html/render/entry-{}.mii'.format(entryno)
	if not exists(mii_filename):
		with open(mii_filename, 'wb') as f:
			miidata = decodeMii(row[i][0])[:-2]
			miidata = miidata[:28] + b'\x00\x00\x00\x00' + miidata[32:] #remove mac address from mii data
			f.write(miidata)

	# if not exists(mii_filename + '.png'):
	#	call(['mono', '/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/MiiRender.exe', mii_filename], stdout = DEVNULL)

	if len(initial) == 1:
		initial += '.'
	elif len(initial) == 2:
		initial = initial[0] + '.' + initial[1] + '.'

	if bool(row[i][6]):
		artisan += '<br><img width = 125 src="https://miicontest.wii.rc24.xyz/images/master.png" />'

	longentry = query[:4] + '-' + query[4:8] + '-' + query[8:12]
	table += '\t<tr>\n'
	table += f'\t\t<td><a href="https://miicontest.wii.rc24.xyz/render/entry-{entryno}.mii"><img width="75" src="{wii2studio(mii_filename)}"/></a></td>\n'
	table += f'\t\t<td>{row[i][4]}</td>\n'
	table += f'\t\t<td>{longentry}</td>\n'
	table += f'\t\t<td>{initial}</td>\n'
	table += f'\t\t<td>{row[i][3]}</td>\n'
	table += f'\t\t<td><a href="https://miicontestp.wii.rc24.xyz/cgi-bin/htmlcraftsearch.cgi?query={row[i][7]}">{artisan}</a></td>\n'
	table += '\t</tr>\n'

table += '</table>\n'

print(head)
print(table)
print('\n</body>\n')
