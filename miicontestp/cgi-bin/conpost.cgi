#!/usr/bin/env python3
from sys import stdout
from cgi import FieldStorage
from html import escape
from base64 import b64encode
from os import environ
import MySQLdb
from json import load
import lz4.block
from crc16 import crc16xmodem
from subprocess import check_output
#import sentry_sdk

with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
    config = load(f)

#sentry_sdk.init(config["sentry_url"])


def result(id):
    stdout.flush()
    stdout.buffer.write(b"X-RESULT: " + str(id).encode() + b"\n\n")
    stdout.flush()
    exit()


def checkWiino(wiino):
    try:
        int(wiino)  # prevents RCE
    except ValueError:
        return False

    wiino = str(wiino).zfill(16)
    if len(wiino) > 16:
        return False
    else:
        checkResult = check_output(
            "wiino check {}".format(wiino), shell=True, universal_newlines=True
        )
        if int(checkResult) == 0:
            return True
        else:
            return False


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


def encodeMii(data):  # takes binary mii data, returns compressed and b64 encoded data
    return b64encode(lz4.block.compress(data, store_size=False)).decode()


form = FieldStorage(
    errors="surrogateescape"
)  # surrogateescape is used to get binary data in forms that are mixed with string data

db = MySQLdb.connect(
    "localhost", config["dbuser"], config["dbpass"], "rc24_cmoc", charset="utf8mb4"
)
cursor = db.cursor()
contestno = form["contestno"].value
craftsno = form["craftsno"].value
macadr = form["macadr"].value
wiino = form["wiino"].value
country = form["country"].value
miidata = (
    form["miidata"].file.read().encode("utf-8", "surrogateescape")
)  # hack to base64 encode multipart form embedded binary
ip = escape(environ["REMOTE_ADDR"])
firstPost = True

cursor.execute("SELECT status FROM contests WHERE id = %s", [contestno])
if (
    cursor.fetchone()[0] != "open"
):  # prevent posting on a contest not accepting new posts
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(
        bytes.fromhex(
            "435000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF"
        )
    )
    stdout.flush()
    exit()

if len(miidata) != 76:
    result(604)
if verifyMac(macadr) == False:
    result(603)
if checkWiino(wiino) == False:
    result(611)

"""crc1 = int.from_bytes(miidata[-2:], "big")  # crc16 that CMOC sends to the server
crc2 = crc16xmodem(miidata[:-2])  # recalculated crc16 that the server confirms
if crc1 != crc2:
    result(605)"""

miidata = encodeMii(miidata)

cursor.execute("SELECT craftsno FROM artisan WHERE mac = %s", [macadr])
storedCraftsno = cursor.fetchall()
verified = False
if len(storedCraftsno) == 0:
    result(607)  # no artisan with this registered mac address

else:
    for c in storedCraftsno:
        if int(c[0]) == int(craftsno):
            verified = True

# if not verified:
#    result(606)  # mac address belongs to another artisan

cursor.execute("SELECT COUNT(*) FROM artisan WHERE wiino = %s", [int(wiino)])
if cursor.fetchone()[0] == 0:
    result(601)  # no artisan with this registered wii number

else:
    cursor.execute("SELECT craftsno FROM artisan WHERE wiino = %s", [int(wiino)])
    if craftsno not in str(cursor.fetchall()):
        result(601)  # wii number belongs to another artisan

cursor.execute(
    "SELECT COUNT(*) FROM conmiis WHERE mac = %s AND contest = %s", (macadr, contestno)
)
if cursor.fetchone()[0] != 0:
    firstPost = False  # this MAC already posted to this contest

cursor.execute(
    "SELECT COUNT(*) FROM conmiis WHERE craftsno = %s AND contest = %s",
    (craftsno, contestno),
)
if cursor.fetchone()[0] != 0:
    firstPost = False  # this artisan already posted to this contest

if firstPost:  # this is a new contest entry
    cursor.execute(
        "INSERT INTO conmiis (contest, craftsno, country, wiino, mac, ip, miidata) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (contestno, craftsno, country, wiino, macadr, ip, miidata),
    )

else:  # this user is updating their entry
    cursor.execute(
        "SELECT ip FROM conmiis WHERE mac = %s AND contest = %s", (macadr, contestno)
    )
    storedIP = cursor.fetchone()
    if storedIP != None:
        if storedIP[0] == "None":  # allows admins to reset a mii's IP
            pass

        elif storedIP[0] != ip:
            pass
            # result(610) #current IP address is different from the one the mii was initially uploaded with

    else:
        pass
        # result(610)

    cursor.execute(
        "UPDATE conmiis SET miidata = %s, ip = %s WHERE craftsno = %s AND mac = %s AND contest = %s",
        (miidata, ip, craftsno, macadr, contestno),
    )

data = bytes.fromhex(
    "435000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF4E4C001000000001FFFFFFFFFFFFFFFF"
)
stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
stdout.flush()
stdout.buffer.write(data)
stdout.flush()

db.commit()
db.close()
