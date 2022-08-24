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


def verifyMac(mac):  # verify macaddress is valid and from a Wii
    oui = [
        "0009BF",
        "001656",
        "0017AB",
        "00191D",
        "0019FD",
        "001AE9",
        "001B7A",
        "001BEA",
        "001CBE",
        "001DBC",
        "001E35",
        "001EA9",
        "001F32",
        "001FC5",
        "002147",
        "0021BD",
        "00224C",
        "0022AA",
        "0022D7",
        "002331",
        "0023CC",
        "00241E",
        "002444",
        "0024F3",
        "0025A0",
        "002659",
        "002709",
        "0403D6",
        "182A7B",
        "2C10C1",
        "34AF2C",
        "40D28A",
        "40F407",
        "582F40",
        "58BDA3",
        "5C521E",
        "606BFF",
        "64B5C6",
        "78A2A0",
        "7CBB8A",
        "8C56C5",
        "8CCDE8",
        "9458CB",
        "98B6E9",
        "9CE635",
        "A438CC",
        "A45C27",
        "A4C0E1",
        "B87826",
        "B88AEC",
        "B8AE6E",
        "CC9E00",
        "CCFB65",
        "D86BF7",
        "DC68EB",
        "E00C7F",
        "E0E751",
        "E84ECE",
        "ECC40D",
    ]
    if len(mac) == 12 and mac.upper()[:6] in oui:
        return True
    else:
        return False


def return403():
    stdout.flush()
    stdout.buffer.write(b"Status: 403 Forbidden\n\n")
    stdout.flush()
    exit()


form = FieldStorage()
db = MySQLdb.connect(
    "localhost", config["dbuser"], config["dbpass"], "rc24_cmoc", charset="utf8mb4"
)
cursor = db.cursor()
# action = form['action'].value
entryno = form["entryno"].value
craftsno = form["craftsno"].value
macadr = form["macadr"].value
ip = escape(environ["REMOTE_ADDR"])

if verifyMac(macadr) == False:
    return403()

cursor.execute("SELECT COUNT(*) FROM artisan WHERE mac = %s", [macadr])
if cursor.fetchone()[0] == 0:
    return403()

cursor.execute("SELECT COUNT(*) FROM mii WHERE entryno = %s", [entryno])
if cursor.fetchone()[0] == 0:  # no result for provided entryno
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(
        bytes.fromhex(
            "565400000000000000000000000000000000000000000000ffffffffffffffff454e002000000001000000010000000100000001000000010000000100000001"
        )
    )
    stdout.flush()
    exit()

cursor.execute(
    "SELECT COUNT(*) FROM votes WHERE mac = %s AND entryno = %s OR ip = %s AND entryno = %s", (macadr, entryno, ip, entryno)
)
if cursor.fetchone()[0] == 0:  # this mac address has not voted on this mii before
    cursor.execute(
        "UPDATE mii SET likes = likes+1, permlikes = permlikes+1 WHERE entryno = %s",
        [entryno],
    )
    cursor.execute(
        "SELECT ROUND(AVG(permlikes)) FROM mii WHERE craftsno=%s", [craftsno]
    )

    average = cursor.fetchone()[0]

    if int(average) < 127:
        cursor.execute(
            "UPDATE artisan SET popularity = %s, votes = votes+1 WHERE craftsno=%s",
            (average, craftsno),
        )  # add +1 to total votes and set popularity to their average mii permlikes

    else:
        cursor.execute(
            "UPDATE artisan SET votes = votes+1 WHERE craftsno=%s", [craftsno]
        )  # add +1 to total votes

    cursor.execute("SELECT votes FROM artisan WHERE craftsno = %s", [craftsno])
    if (
        int(cursor.fetchone()[0]) >= 1000
    ):  # 1000 likes needed to become a master artisan
        cursor.execute("UPDATE artisan SET master = 1 WHERE craftsno  = %s", [craftsno])

    cursor.execute(
        "INSERT INTO votes (mac, ip, entryno, craftsno) VALUES (%s, %s, %s, %s)",
        [macadr, ip, entryno, craftsno],
    )  # log their vote

    data = bytes.fromhex(
        "565400000000000000000000000000000000000000000000ffffffffffffffff454e002000000001000000010000000100000001000000010000000100000001"
    )
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(data)
    stdout.flush()
    db.commit()
    db.close()

else:  # duplicate vote, piss off
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(
        bytes.fromhex(
            "565400000000000000000000000000000000000000000000ffffffffffffffff454e002000000001000000010000000100000001000000010000000100000001"
        )
    )
    stdout.flush()

    exit()
