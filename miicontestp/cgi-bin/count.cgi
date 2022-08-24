#!/usr/bin/env python3
from sys import stdout
from cgi import FieldStorage
from html import escape
import MySQLdb
from json import load
from os import environ
#import sentry_sdk

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
    config = load(f)

#sentry_sdk.init(config["sentry_url"])



form = FieldStorage()
db = MySQLdb.connect(
    "localhost", config["dbuser"], config["dbpass"], "rc24_cmoc", charset="utf8mb4"
)
cursor = db.cursor()
# action = form['action'].value
cursor.execute('SELECT COUNT(*) FROM mii')
count = int(cursor.fetchone()[0])

stdout.buffer.write(b"Content-Type:text/plain\n\n")

stdout.buffer.write(b"Total Miis in Database: " + str(count).encode("utf-8") + b"\n")
stdout.flush()

form = FieldStorage()
db = MySQLdb.connect(
    "localhost", config["dbuser"], config["dbpass"], "rc24_mail", charset="utf8mb4"
)
cursor = db.cursor()
# action = form['action'].value
cursor.execute('SELECT COUNT(*) FROM accounts')
count = int(cursor.fetchone()[0])

stdout.buffer.write(b"Total Mail Accounts in Database: " + str(count).encode("utf-8"))
stdout.flush()
