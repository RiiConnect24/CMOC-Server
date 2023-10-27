#!/usr/bin/env python3
import cgi, cgitb

# cgitb.enable()
import MySQLdb
import lz4.block
from base64 import b64decode
from os.path import exists
from subprocess import call, DEVNULL
from json import load
from cmoc import wii2studio

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
    if (num > 0xD4A50FFF) + (crc & 0xFF) > 232:
        crc &= 0x7F

    crc &= 0xFF
    return str(int((format(crc, "08b") + format(num, "032b")), 2)).zfill(12)


print("Content-type:text/html\r\n\r\n")

form = cgi.FieldStorage()
query = form.getvalue("query")
db = MySQLdb.connect(
    "localhost",
    config["dbuser"],
    config["dbpass"],
    "rc24_cmoc",
    use_unicode=True,
    charset="utf8mb4",
)
cursor = db.cursor()

headers = ["Mii", "Entry Number", "Nickname", "Initials", "Likes"]
for h in range(len(headers)):
    headers[h] = "\t\t<th>" + headers[h] + "</th>\n"
headers = "\t<tr>\n" + "".join(headers) + "\t</tr>\n"

cursor.execute("SELECT nickname FROM artisan WHERE craftsno = %s", [query])
try:
    craftName = cursor.fetchone()[0]
except TypeError:
    print(
        '<!DOCTYPE html>\n<html>\n<head>\n<title>Mii Search</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">\n<link href="https://miicontest.wii.rc24.xyz/css/style.css" rel="Stylesheet" type="text/css" />\n<link href="https://miicontest.wii.rc24.xyz/css/ctmkf.css" rel="Stylesheet" type="text/css" />\n<link rel="apple-touch-icon" sizes="180x180" href="https://miicontest.wii.rc24.xyz/apple-touch-icon.png">\n<link rel="icon" type="image/png" sizes="32x32" href="https://miicontest.wii.rc24.xyz/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="16x16" href="https://miicontest.wii.rc24.xyz/favicon-16x16.png">\n<link rel="manifest" href="https://miicontest.wii.rc24.xyz/site.webmanifest">\n<link rel="mask-icon" href="https://miicontest.wii.rc24.xyz/safari-pinned-tab.svg" color="#89c0ca">\n<meta name="msapplication-TileColor" content="#2d89ef">\n<meta name="theme-color" content="#c57725">\n<!-- General Meta tags for SEO -->\n<meta name="language" content="en">\n<meta name="title" content="Check Mii Out Channel" />\n<meta name="author" content="RiiConnect24" />\n<meta name="copyright" content="&copy; RiiConnect24" />\n<meta name="robots" content="index, follow" />\n<meta name="subject" content="Mii">\n<meta name="keywords" content="Nintendo, Wii, Homebrew, WiiConnect24, Mii, Contest">\n<meta name="description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<meta name="classification" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Open Graph Tags -->\n<meta property="og:type" content="website" />\n<meta property="og:title" content="Check Mii Out Channel" />\n<meta property="og:image" content="https://miicontest.wii.rc24.xyz/images/banner.png" />\n<meta property="og:locale" content="en" />\n<meta property="og:site_name" content="Check Mii Out Channel" />\n<meta property="og:description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Twitter -->\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:site" content="@RiiConnect24">\n<meta name="twitter:creator" content="@RiiConnect24">\n\n<meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>\n\n<body class="center">\n<h2><img width=60 src="https://miicontest.wii.rc24.xyz/search/search.png"> Mii Search by Artisan</h2>'
    )
    print("Mii Artisan not found.")
    exit()

cursor.execute(
    "SELECT miidata, entryno, initial, permlikes, nickname FROM mii WHERE craftsno = %s ORDER BY permlikes DESC LIMIT 300",
    [query],
)
row = cursor.fetchall()

head = f'<!DOCTYPE html>\n<html>\n<head>\n<title>Miis created by {craftName}</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">\n<link href="https://miicontest.wii.rc24.xyz/css/style.css" rel="Stylesheet" type="text/css" />\n<link href="https://miicontest.wii.rc24.xyz/css/ctmkf.css" rel="Stylesheet" type="text/css" />\n<link rel="apple-touch-icon" sizes="180x180" href="https://miicontest.wii.rc24.xyz/apple-touch-icon.png">\n<link rel="icon" type="image/png" sizes="32x32" href="https://miicontest.wii.rc24.xyz/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="16x16" href="https://miicontest.wii.rc24.xyz/favicon-16x16.png">\n<link rel="manifest" href="https://miicontest.wii.rc24.xyz/site.webmanifest">\n<link rel="mask-icon" href="https://miicontest.wii.rc24.xyz/safari-pinned-tab.svg" color="#89c0ca">\n<meta name="msapplication-TileColor" content="#2d89ef">\n<meta name="theme-color" content="#c57725">\n<!-- General Meta tags for SEO -->\n<meta name="language" content="en">\n<meta name="title" content="Check Mii Out Channel" />\n<meta name="author" content="RiiConnect24" />\n<meta name="copyright" content="&copy; RiiConnect24" />\n<meta name="robots" content="index, follow" />\n<meta name="subject" content="Mii">\n<meta name="keywords" content="Nintendo, Wii, Homebrew, WiiConnect24, Mii, Contest">\n<meta name="description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<meta name="classification" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Open Graph Tags -->\n<meta property="og:type" content="website" />\n<meta property="og:title" content="Check Mii Out Channel" />\n<meta property="og:image" content="https://miicontest.wii.rc24.xyz/images/banner.png" />\n<meta property="og:locale" content="en" />\n<meta property="og:site_name" content="Check Mii Out Channel" />\n<meta property="og:description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Twitter -->\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:site" content="@RiiConnect24">\n<meta name="twitter:creator" content="@RiiConnect24">\n</head>\n\n<body class="center">\n<h2><img width=60 src="https://miicontest.wii.rc24.xyz/search/search.png"> Mii Search by Artisan</h2>'
table = (
    f'<p>{len(row)} Miis created by <b>{craftName}</b></p>\n<p>Click on a Mii to download it.</p>\n<table class="striped" align="center">\n'
    + headers
)

for i in range(len(row)):
    entryno = row[i][1]
    initial = row[i][2]
    mii_filename = f"/var/www/rc24/wapp.wii.com/miicontest/public_html/render/entry-{entryno}.mii"
    if not exists(mii_filename):
        with open(mii_filename, "wb") as f:
            miidata = decodeMii(row[i][0])[:-2]
            miidata = (
                miidata[:28] + b"\x00\x00\x00\x00" + miidata[32:]
            )  # remove mac address from mii data
            f.write(miidata)

            # if not exists(mii_filename + '.png'):
            # 	call(['mono', '/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/MiiRender.exe', mii_filename], stdout = DEVNULL)

    if len(initial) == 1:
        initial += "."
    elif len(initial) == 2:
        initial = f"{initial[0]}.{initial[1]}."

    longentry = decToEntry(entryno)
    longentry = f"{longentry[:4]}-{longentry[4:8]}-{longentry[8:12]}"
    table += "\t<tr>\n"
    table += f'\t\t<td><a href="https://miicontest.wii.rc24.xyz/render/entry-{entryno}.mii"><img width="75" src="{wii2studio(mii_filename)}"/></a></td>\n'
    table += f"\t\t<td>{longentry}</td>\n"
    table += f"\t\t<td>{row[i][4]}</td>\n"
    table += f"\t\t<td>{initial}</td>\n"
    table += f"\t\t<td>{row[i][3]}</td>\n"
    table += "\t</tr>\n"

table += "</table>\n"

print(head)
print(table)

if len(row) > 300:
    print(
        f"<p>Up to 300 Miis can be displayed at a time. {len(row) - 300} Miis are not shown.</p>"
    )

print("\n</body>\n")
