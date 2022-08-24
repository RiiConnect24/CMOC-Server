#!/usr/bin/env python3
from sys import stdout
from cgi import FieldStorage
from struct import pack
from binascii import hexlify, unhexlify
from gen1_wii import Gen1Wii
import pycurl
from io import BytesIO
#import sentry_sdk

#with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
#   config = load(f)

#sentry_sdk.init(config["sentry_url"])

form = FieldStorage()

orig_mii = Gen1Wii.from_bytes(unhexlify(form["data"].value))


def u8(data):
    return pack(">B", data)


studio_mii = {}

makeup = {1: 1, 2: 6, 3: 9, 9: 10}  # lookup table

wrinkles = {4: 5, 5: 2, 6: 3, 7: 7, 8: 8, 10: 9, 11: 11}  # lookup table

# we generate the Mii Studio file by reading each Mii format from the Kaitai files.
# unlike consoles which store Mii data in an odd number of bits,
# all the Mii data for a Mii Studio Mii is stored as unsigned 8-bit integers. makes it easier.

if orig_mii.facial_hair_color == 0:
    studio_mii["facial_hair_color"] = 8
else:
    studio_mii["facial_hair_color"] = orig_mii.facial_hair_color
studio_mii["beard_goatee"] = orig_mii.facial_hair_beard
studio_mii["body_weight"] = orig_mii.body_weight
studio_mii["eye_stretch"] = 3
studio_mii["eye_color"] = orig_mii.eye_color + 8
studio_mii["eye_rotation"] = orig_mii.eye_rotation
studio_mii["eye_size"] = orig_mii.eye_size
studio_mii["eye_type"] = orig_mii.eye_type
studio_mii["eye_horizontal"] = orig_mii.eye_horizontal
studio_mii["eye_vertical"] = orig_mii.eye_vertical
studio_mii["eyebrow_stretch"] = 3
if orig_mii.eyebrow_color == 0:
    studio_mii["eyebrow_color"] = 8
else:
    studio_mii["eyebrow_color"] = orig_mii.eyebrow_color
studio_mii["eyebrow_rotation"] = orig_mii.eyebrow_rotation
studio_mii["eyebrow_size"] = orig_mii.eyebrow_size
studio_mii["eyebrow_type"] = orig_mii.eyebrow_type
studio_mii["eyebrow_horizontal"] = orig_mii.eyebrow_horizontal
studio_mii["eyebrow_vertical"] = orig_mii.eyebrow_vertical
studio_mii["face_color"] = orig_mii.face_color
if orig_mii.facial_feature in makeup:
    studio_mii["face_makeup"] = makeup[orig_mii.facial_feature]
else:
    studio_mii["face_makeup"] = 0
studio_mii["face_type"] = orig_mii.face_type
if orig_mii.facial_feature in wrinkles:
    studio_mii["face_wrinkles"] = wrinkles[orig_mii.facial_feature]
else:
    studio_mii["face_wrinkles"] = 0
studio_mii["favorite_color"] = orig_mii.favorite_color
studio_mii["gender"] = orig_mii.gender
if orig_mii.glasses_color == 0:
    studio_mii["glasses_color"] = 8
elif orig_mii.glasses_color < 6:
    studio_mii["glasses_color"] = orig_mii.glasses_color + 13
else:
    studio_mii["glasses_color"] = 0
studio_mii["glasses_size"] = orig_mii.glasses_size
studio_mii["glasses_type"] = orig_mii.glasses_type
studio_mii["glasses_vertical"] = orig_mii.glasses_vertical
if orig_mii.hair_color == 0:
    studio_mii["hair_color"] = 8
else:
    studio_mii["hair_color"] = orig_mii.hair_color
studio_mii["hair_flip"] = orig_mii.hair_flip
studio_mii["hair_type"] = orig_mii.hair_type
studio_mii["body_height"] = orig_mii.body_height
studio_mii["mole_size"] = orig_mii.mole_size
studio_mii["mole_enable"] = orig_mii.mole_enable
studio_mii["mole_horizontal"] = orig_mii.mole_horizontal
studio_mii["mole_vertical"] = orig_mii.mole_vertical
studio_mii["mouth_stretch"] = 3
if orig_mii.mouth_color < 4:
    studio_mii["mouth_color"] = orig_mii.mouth_color + 19
else:
    studio_mii["mouth_color"] = 0
studio_mii["mouth_size"] = orig_mii.mouth_size
studio_mii["mouth_type"] = orig_mii.mouth_type
studio_mii["mouth_vertical"] = orig_mii.mouth_vertical
studio_mii["beard_size"] = orig_mii.facial_hair_size
studio_mii["beard_mustache"] = orig_mii.facial_hair_mustache
studio_mii["beard_vertical"] = orig_mii.facial_hair_vertical
studio_mii["nose_size"] = orig_mii.nose_size
studio_mii["nose_type"] = orig_mii.nose_type
studio_mii["nose_vertical"] = orig_mii.nose_vertical

mii_data = b""
n = r = 256
mii_dict = studio_mii.values()
mii_data += hexlify(u8(0))
for v in mii_dict:
    eo = (
        7 + (v ^ n)
    ) % 256  # encode the Mii, Nintendo seemed to have randomized the encoding using Math.random() in JS, but we removed randomizing
    n = eo
    mii_data += hexlify(u8(eo))

buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, "https://studio.mii.nintendo.com/miis/image.png?data="
    + mii_data.decode("utf-8")
    + "&type=face&width=512&instanceCount=1")
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()

mii = buffer.getvalue()

stdout.buffer.write(b"Content-Type:image/png\n\n")
stdout.flush()
stdout.buffer.write(mii)
