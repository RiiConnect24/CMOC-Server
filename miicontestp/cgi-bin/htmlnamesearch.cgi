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

head = f'<!DOCTYPE html>\n<html>\n<head>\n<title>Artisan Search</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">\n<link href="https://miicontest.wii.rc24.xyz/css/style.css" rel="Stylesheet" type="text/css" />\n<link href="https://miicontest.wii.rc24.xyz/css/ctmkf.css" rel="Stylesheet" type="text/css" />\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/flag-icon-css/2.8.0/css/flag-icon.min.css" />\n<link rel="apple-touch-icon" sizes="180x180" href="https://miicontest.wii.rc24.xyz/apple-touch-icon.png">\n<link rel="icon" type="image/png" sizes="32x32" href="https://miicontest.wii.rc24.xyz/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="16x16" href="https://miicontest.wii.rc24.xyz/favicon-16x16.png">\n<link rel="manifest" href="https://miicontest.wii.rc24.xyz/site.webmanifest">\n<link rel="mask-icon" href="https://miicontest.wii.rc24.xyz/safari-pinned-tab.svg" color="#89c0ca">\n<meta name="msapplication-TileColor" content="#2d89ef">\n<meta name="theme-color" content="#c57725">\n<!-- General Meta tags for SEO -->\n<meta name="language" content="en">\n<meta name="title" content="Artisan Search" />\n<meta name="author" content="RiiConnect24" />\n<meta name="copyright" content="&copy; RiiConnect24" />\n<meta name="robots" content="index, follow" />\n<meta name="subject" content="Mii">\n<meta name="keywords" content="Nintendo, Wii, Homebrew, WiiConnect24, Mii, Contest">\n<meta name="description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<meta name="classification" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Open Graph Tags -->\n<meta property="og:type" content="website" />\n<meta property="og:title" content="Artisan Search" />\n<meta property="og:image" content="https://miicontest.wii.rc24.xyz/images/banner.png" />\n<meta property="og:locale" content="en" />\n<meta property="og:site_name" content="Check Mii Out Channel" />\n<meta property="og:description" content="You can view and download Miis posted to our Check Mii Out Channel revival here. It\'s like Super Mario Maker Bookmark, but about Miis.">\n<!-- Twitter -->\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:site" content="@RiiConnect24">\n<meta name="twitter:creator" content="@RiiConnect24">\n\n<meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>\n\n<body class="center">\n<h2><img width=60 src="https://miicontest.wii.rc24.xyz/search/search.png"> Artisan Search</h2>'
countries = {
    1: "jp",
    8: "ai",
    9: "ag",
    10: "ar",
    11: "aw",
    12: "bs",
    13: "bb",
    14: "bz",
    15: "bo",
    16: "br",
    17: "vg",
    18: "ca",
    19: "ky",
    20: "cl",
    21: "co",
    22: "cr",
    23: "dm",
    24: "do",
    25: "ec",
    26: "sv",
    27: "gf",
    28: "gd",
    29: "gp",
    30: "gt",
    31: "gy",
    32: "ht",
    33: "hn",
    34: "jm",
    35: "mq",
    36: "mx",
    37: "ms",
    38: "cw",
    39: "ni",
    40: "pa",
    41: "py",
    42: "pe",
    43: "kn",
    44: "lc",
    45: "vc",
    46: "sr",
    47: "tt",
    48: "tc",
    49: "us",
    50: "uy",
    51: "vi",
    52: "ve",
    64: "al",
    65: "au",
    66: "at",
    67: "be",
    68: "ba",
    69: "bw",
    70: "bg",
    71: "hr",
    72: "cy",
    73: "cz",
    74: "dk",
    75: "ee",
    76: "fi",
    77: "fr",
    78: "de",
    79: "gr",
    80: "hu",
    81: "is",
    82: "ie",
    83: "it",
    84: "lv",
    85: "ls",
    86: "li",
    87: "lt",
    88: "lu",
    89: "mk",
    90: "mt",
    91: "me",
    92: "mz",
    93: "na",
    94: "nl",
    95: "nz",
    96: "no",
    97: "pl",
    98: "pt",
    99: "ro",
    100: "ru",
    101: "rs",
    102: "sk",
    103: "si",
    104: "za",
    105: "es",
    106: "sz",
    107: "se",
    108: "ch",
    109: "tr",
    110: "gb",
    111: "zm",
    112: "zw",
    113: "az",
    114: "mr",
    115: "ml",
    116: "ne",
    117: "td",
    118: "sd",
    119: "er",
    120: "dj",
    121: "so",
    128: "tw",
    136: "kr",
    144: "hk",
    145: "mo",
    152: "id",
    153: "sg",
    154: "th",
    155: "ph",
    156: "my",
    160: "cn",
    168: "ae",
    169: "in",
    170: "eg",
    171: "om",
    172: "qa",
    173: "kw",
    174: "sa",
    175: "sy",
    176: "bh",
    177: "jo",
}

headers = ["Rank", "Mii", "Artisan", "Votes", "Posts"]
for h in range(len(headers)):
    headers[h] = "\t\t<th>" + headers[h] + "</th>\n"
headers = "\t<tr>\n" + "".join(headers) + "\t</tr>\n"

cursor.execute(
    "SELECT COUNT(*) FROM artisan WHERE nickname LIKE %s", ["%" + query + "%"]
)
count = cursor.fetchone()[0]
if count == 0:
    print(head)
    print(f"No results found for <b>{query}</b>.")
    exit()

cursor.execute(
    "SELECT artisan.craftsno, artisan.miidata, artisan.nickname, artisan.country, artisan.votes, (SELECT COUNT(*) FROM mii WHERE mii.craftsno = artisan.craftsno) as posts FROM artisan WHERE artisan.nickname LIKE %s ORDER BY posts DESC LIMIT 100",
    ["%" + query + "%"],
)
row = cursor.fetchall()

table = (
    f'<p>{count} Artisans named <b>{query}</b></p>\n<p>Click on a Mii to download it.</p>\n<table class="striped" align="center">\n'
    + headers
)

for i in range(len(row)):
    master = ""
    craftsno = row[i][0]
    nickname = row[i][2]
    mii_filename = "/var/www/rc24/wapp.wii.com/miicontest/public_html/render/crafts-{}.mii".format(
        craftsno
    )
    if not exists(mii_filename):
        with open(mii_filename, "wb") as f:
            miidata = decodeMii(row[i][1])[:-2]
            miidata = (
                miidata[:28] + b"\x00\x00\x00\x00" + miidata[32:]
            )  # remove mac address from mii data
            f.write(miidata)

            # if not exists(mii_filename + '.png'):
            # 	call(['mono', '/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/MiiRender.exe', mii_filename], stdout = DEVNULL)

    if int(row[i][4]) >= 1000:
        master = '<img src="https://miicontest.wii.rc24.xyz/images/master.png" /><br>'

    try:
        country = (
            '<span class="flag-icon flag-icon-' + countries[row[i][3]] + '"></span> '
        )

    except KeyError:
        country = ""

    table += "\t<tr>\n"
    table += f"\t\t<td>{i + 1}</td>\n"
    table += f'\t\t<td><a href="https://miicontest.wii.rc24.xyz/render/crafts-{craftsno}.mii"><img width="75" src="{wii2studio(mii_filename)}"/></a></td>\n'
    table += f'\t\t<td><a href="https://miicontestp.wii.rc24.xyz/cgi-bin/htmlcraftsearch.cgi?query={craftsno}">{country + nickname}<br>{master}</a></td>\n'
    table += f"\t\t<td>{row[i][4]}</td>\n"
    table += f"\t\t<td>{row[i][5]}</td>\n"
    table += "\t</tr>\n"

table += "</table>\n"

print(head)
print(table)

if count > 100:
    print(
        f"<p>Up to 100 results can be displayed at a time. {count - 100} results are not shown.</p>"
    )

print("\n</body>\n")
