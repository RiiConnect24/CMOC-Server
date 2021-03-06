#!/usr/bin/env python
import cgi
import cgitb

# cgitb.enable()
import MySQLdb
import lz4.block
from base64 import b64decode
from os.path import exists
from subprocess import call, DEVNULL
from json import load
from cmoc import wii2studio
from datetime import datetime

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
    config = load(f)


def decodeMii(data):  # takes compressed and b64 encoded data, returns binary mii data
    return lz4.block.decompress(b64decode(data.encode()), uncompressed_size=76)


def decToEntry(
    num: int
) -> str:  # takes decimal int, outputs 12 digit entry number string
    num ^= ((num << 0x1E) ^ (num << 0x12) ^ (num << 0x18)) & 0xFFFFFFFF
    num ^= (num & 0xF0F0F0F) << 4
    num ^= (num >> 0x1D) ^ (num >> 0x11) ^ (num >> 0x17) ^ 0x20070419

    crc = (num >> 8) ^ (num >> 24) ^ (num >> 16) ^ (num & 0xFF) ^ 0xFF
    if 232 < (0xD4A50FFF < num) + (crc & 0xFF):
        crc &= 0x7F

    crc &= 0xFF
    return str(int((format(crc, "08b") + format(num, "032b")), 2)).zfill(12)


print("Content-type:text/html\r\n\r\n")

form = cgi.FieldStorage()
db = MySQLdb.connect(
    "localhost",
    config["dbuser"],
    config["dbpass"],
    "cmoc",
    use_unicode=True,
    charset="utf8mb4",
)
cursor = db.cursor()

headers = ["Contest", "Topic", "Start Date"]
for h in range(len(headers)):
    headers[h] = "\t\t<th>" + headers[h] + "</th>\n"
headers = "\t<tr>\n" + "".join(headers) + "\t</tr>\n"

cursor.execute(
    'SELECT id,description,topic,start,status FROM contests WHERE status = "closed" OR status = "results" ORDER BY id'
)
row = cursor.fetchall()

head = f'<!DOCTYPE html>\n<html>\n<head>\n<title>Contest List</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">\n<link href="https://miicontest.wii.rc24.xyz/css/style.css" rel="Stylesheet" type="text/css" />\n<link href="https://miicontest.wii.rc24.xyz/css/ctmkf.css" rel="Stylesheet" type="text/css" />\n<link rel="apple-touch-icon" sizes="180x180" href="https://miicontest.wii.rc24.xyz/apple-touch-icon.png">\n<link rel="icon" type="image/png" sizes="32x32" href="https://miicontest.wii.rc24.xyz/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="16x16" href="https://miicontest.wii.rc24.xyz/favicon-16x16.png">\n<link rel="manifest" href="https://miicontest.wii.rc24.xyz/site.webmanifest">\n<link rel="mask-icon" href="https://miicontest.wii.rc24.xyz/safari-pinned-tab.svg" color="#89c0ca">\n<meta name="msapplication-TileColor" content="#2d89ef">\n<meta name="theme-color" content="#ffffff">\n</head>\n\n<body class="center">\n<h2><img src="https://miicontest.wii.rc24.xyz/images/rankings.png" id="icon"> Contest List</h2>'
table = f'<table class="striped" align="center">\n' + headers

for i in range(len(row)):
    id = row[i][0]
    description = row[i][1]
    topic = row[i][2]
    start = datetime.fromtimestamp(946_684_800 + row[i][3]).strftime("%Y-%m-%d")

    table += "\t<tr>\n"
    table += f'\t\t<td><a href="/cgi-bin/htmlcontestsearch.cgi?query={id}">{description}</a></td>\n'
    table += f"\t\t<td>{topic}</td>\n"
    table += f"\t\t<td>{start}</td>\n"
    table += "\t</tr>\n"

table += "</table>\n"

print(head)
print(table)

print("\n</body>\n")
