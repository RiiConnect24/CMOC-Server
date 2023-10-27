#!/usr/bin/env python3
from cgi import FieldStorage
from sys import stdout
from cmoc import ConResult
import MySQLdb
from json import load
from sys import stdout
#import sentry_sdk

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
    config = load(f)

#sentry_sdk.init(config["sentry_url"])


def result(id):
    stdout.flush()
    stdout.buffer.write(b"X-RESULT: " + str(id).encode() + b"\n\n")
    stdout.flush()
    exit()


db = MySQLdb.connect(
    "localhost", config["dbuser"], config["dbpass"], "rc24_cmoc", charset="utf8mb4"
)
cursor = db.cursor()
cr = ConResult()
form = FieldStorage()
contestno = form["contestno"].value

artisans = []
try:  # bangladesh code but it works
    artisans.extend(
        (
            form["craftsno1"].value,
            form["craftsno2"].value,
            form["craftsno3"].value,
        )
    )
    judgingMiis = True

except KeyError:
    artisans.append(form["craftsno1"].value)
    judgingMiis = False

if judgingMiis:
    try:
        artisans.append(form["craftsno4"].value)

    except KeyError:
        pass

miilist = []
for i in artisans:
    cursor.execute(
        "SELECT `rank` FROM conmiis WHERE craftsno = %s AND contest = %s",
        (i, contestno),
    )
    try:
        rank = cursor.fetchone()[0]
        miilist.append((int(i), int(rank)))
    except:
        miilist.append((int(i), 0))

data = cr.build(int(contestno), miilist)
stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
stdout.flush()

db.close()
