#!/usr/bin/env python3
from cgi import FieldStorage
from html import escape
from os import environ
from sys import stdout
import MySQLdb
from json import load
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


def result(id):
    stdout.flush()
    stdout.buffer.write(b"X-RESULT: " + str(id).encode() + b"\n\n")
    stdout.flush()
    exit()


def returnFail():
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(
        bytes.fromhex(
            "435600000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF"
        )
    )
    stdout.flush()


def returnPass():
    stdout.buffer.write(b"Content-Type:application/octet-stream\n\n")
    stdout.flush()
    stdout.buffer.write(
        bytes.fromhex(
            "435600000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF4E4C001000000001FFFFFFFFFFFFFFFF"
        )
    )
    stdout.flush()


returnPass()
