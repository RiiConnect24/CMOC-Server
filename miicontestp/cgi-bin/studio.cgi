#!/usr/bin/env python3
from sys import stdout, stderr
from binascii import hexlify
from cgi import FieldStorage
from json import load, dumps
from struct import pack

# import sentry_sdk

# with open("/var/rc24/File-Maker/Channels/Check_Mii_Out_Channel/config.json", "r") as f:
#   config = load(f)

# sentry_sdk.init(config["sentry_url"])

form = FieldStorage()

input_type = form["platform"].value

try:
    input_data = form["data"].value
except:
    input_data = b""
    id = form["id"].value

try:
    if input_type == "wii":
        from gen1_wii import Gen1Wii

        try:
            if input_data == b"":
                num = int(
                    format(int(id.strip().replace("-", "")), "032b").zfill(40)[8:], 2
                )  # the cmoc entry numbr is scrambled using a lot of bitwise operations
                num ^= 0x20070419
                num ^= (num >> 0x1D) ^ (num >> 0x11) ^ (num >> 0x17)
                num ^= (num & 0xF0F0F0F) << 4
                num ^= ((num << 0x1E) ^ (num << 0x12) ^ (num << 0x18)) & 0xFFFFFFFF

                stderr.write(str(num))

                import pycurl
                from io import BytesIO

                buffer = BytesIO()
                c = pycurl.Curl()
                c.setopt(
                    c.URL,
                    "https://miicontestp.wii.rc24.xyz/cgi-bin/search.cgi?entryno="
                    + str(num),
                )
                c.setopt(c.WRITEDATA, buffer)
                c.perform()
                c.close()

                query = buffer.getvalue()
                stderr.write(hexlify(query).decode("utf-8"))

                if len(query) != 32:  # 32 = empty response
                    mii = query[56:130]  # cut the Mii out of the file
                else:
                    print("Mii not found.")
            else:
                mii = input_data
        except ValueError as e:
            raise e

        orig_mii = Gen1Wii.from_bytes(mii)
    elif (
        input_type == "gen2"
        or input_type == "3ds"
        or input_type == "wiiu"
        or input_type == "miitomo"
    ):
        from gen2_wiiu_3ds_miitomo import Gen2Wiiu3dsMiitomo
        from Crypto.Cipher import AES

        if (
            input_data[:2] == b"\xFF\xD8" or input_data[:4] == b"\x89PNG"
        ):  # crappy way to detect if input is an mage

            import pycurl
            from io import BytesIO
            from urllib.parse import urlencode

            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(
                c.URL, "https://qrcode.rc24.xyz/qrcode.php"
            )  # zbar sucks to run on a client so we use this api

            post_data = {"image": input_data}
            postfields = urlencode(post_data)
            c.setopt(c.POSTFIELDS, postfields)
            c.setopt(c.WRITEDATA, buffer)

            c.perform()
            c.close()

            decoded_qr = buffer.getvalue()

            # https://gist.github.com/jaames/96ce8daa11b61b758b6b0227b55f9f78

            key = bytes(
                [
                    0x59,
                    0xFC,
                    0x81,
                    0x7E,
                    0x64,
                    0x46,
                    0xEA,
                    0x61,
                    0x90,
                    0x34,
                    0x7B,
                    0x20,
                    0xE9,
                    0xBD,
                    0xCE,
                    0x52,
                ]
            )

            nonce = decoded_qr[:8]
            cipher = AES.new(key, AES.MODE_CCM, nonce + bytes([0, 0, 0, 0]))
            content = cipher.decrypt(decoded_qr[8:96])
            mii = content[:12] + nonce + content[12:]

            input_data = mii

        orig_mii = Gen2Wiiu3dsMiitomo.from_bytes(input_data)
    elif input_type == "switch":
        from gen3_switch import Gen3Switch

        orig_mii = Gen3Switch.from_bytes(input_data)
    elif input_type == "switchgame":
        from gen3_switchgame import Gen3Switchgame

        orig_mii = Gen3Switchgame.from_bytes(input_data)
    elif input_type != "studio":
        exit()

    def u8(data):
        return pack(">B", data)

    if input_type != "studio":
        stdout.flush()

        studio_mii = {}

        makeup = {1: 1, 2: 6, 3: 9, 9: 10}  # lookup table

        wrinkles = {4: 5, 5: 2, 6: 3, 7: 7, 8: 8, 10: 9, 11: 11}  # lookup table

        # we generate the Mii Studio file by reading each Mii format from the Kaitai files.
        # unlike consoles which store Mii data in an odd number of bits,
        # all the Mii data for a Mii Studio Mii is stored as unsigned 8-bit integers. makes it easier.

        if "switch" not in input_type:
            if orig_mii.facial_hair_color == 0:
                studio_mii["facial_hair_color"] = 8
            else:
                studio_mii["facial_hair_color"] = orig_mii.facial_hair_color
        else:
            studio_mii["facial_hair_color"] = orig_mii.facial_hair_color
        studio_mii["beard_goatee"] = orig_mii.facial_hair_beard
        studio_mii["body_weight"] = orig_mii.body_weight
        if input_type == "wii":
            studio_mii["eye_stretch"] = 3
        else:
            studio_mii["eye_stretch"] = orig_mii.eye_stretch
        if "switch" not in input_type:
            studio_mii["eye_color"] = orig_mii.eye_color + 8
        else:
            studio_mii["eye_color"] = orig_mii.eye_color
        studio_mii["eye_rotation"] = orig_mii.eye_rotation
        studio_mii["eye_size"] = orig_mii.eye_size
        studio_mii["eye_type"] = orig_mii.eye_type
        studio_mii["eye_horizontal"] = orig_mii.eye_horizontal
        studio_mii["eye_vertical"] = orig_mii.eye_vertical
        if input_type == "wii":
            studio_mii["eyebrow_stretch"] = 3
        else:
            studio_mii["eyebrow_stretch"] = orig_mii.eyebrow_stretch
        if "switch" not in input_type:
            if orig_mii.eyebrow_color == 0:
                studio_mii["eyebrow_color"] = 8
            else:
                studio_mii["eyebrow_color"] = orig_mii.eyebrow_color
        else:
            studio_mii["eyebrow_color"] = orig_mii.eyebrow_color
        studio_mii["eyebrow_rotation"] = orig_mii.eyebrow_rotation
        studio_mii["eyebrow_size"] = orig_mii.eyebrow_size
        studio_mii["eyebrow_type"] = orig_mii.eyebrow_type
        studio_mii["eyebrow_horizontal"] = orig_mii.eyebrow_horizontal
        if input_type != "switch":
            studio_mii["eyebrow_vertical"] = orig_mii.eyebrow_vertical
        else:
            studio_mii["eyebrow_vertical"] = orig_mii.eyebrow_vertical + 3
        studio_mii["face_color"] = orig_mii.face_color
        if input_type == "wii":
            if orig_mii.facial_feature in makeup:
                studio_mii["face_makeup"] = makeup[orig_mii.facial_feature]
            else:
                studio_mii["face_makeup"] = 0
        else:
            studio_mii["face_makeup"] = orig_mii.face_makeup
        studio_mii["face_type"] = orig_mii.face_type
        if input_type == "wii":
            if orig_mii.facial_feature in wrinkles:
                studio_mii["face_wrinkles"] = wrinkles[orig_mii.facial_feature]
            else:
                studio_mii["face_wrinkles"] = 0
        else:
            studio_mii["face_wrinkles"] = orig_mii.face_wrinkles
        studio_mii["favorite_color"] = orig_mii.favorite_color
        studio_mii["gender"] = orig_mii.gender
        if "switch" not in input_type:
            if orig_mii.glasses_color == 0:
                studio_mii["glasses_color"] = 8
            elif orig_mii.glasses_color < 6:
                studio_mii["glasses_color"] = orig_mii.glasses_color + 13
            else:
                studio_mii["glasses_color"] = 0
        else:
            studio_mii["glasses_color"] = orig_mii.glasses_color
        studio_mii["glasses_size"] = orig_mii.glasses_size
        studio_mii["glasses_type"] = orig_mii.glasses_type
        studio_mii["glasses_vertical"] = orig_mii.glasses_vertical
        if "switch" not in input_type:
            if orig_mii.hair_color == 0:
                studio_mii["hair_color"] = 8
            else:
                studio_mii["hair_color"] = orig_mii.hair_color
        else:
            studio_mii["hair_color"] = orig_mii.hair_color
        studio_mii["hair_flip"] = orig_mii.hair_flip
        studio_mii["hair_type"] = orig_mii.hair_type
        studio_mii["body_height"] = orig_mii.body_height
        studio_mii["mole_size"] = orig_mii.mole_size
        studio_mii["mole_enable"] = orig_mii.mole_enable
        studio_mii["mole_horizontal"] = orig_mii.mole_horizontal
        studio_mii["mole_vertical"] = orig_mii.mole_vertical
        if input_type == "wii":
            studio_mii["mouth_stretch"] = 3
        else:
            studio_mii["mouth_stretch"] = orig_mii.mouth_stretch
        if "switch" not in input_type:
            if orig_mii.mouth_color < 5:
                studio_mii["mouth_color"] = orig_mii.mouth_color + 19
            else:
                studio_mii["mouth_color"] = 0
        else:
            studio_mii["mouth_color"] = orig_mii.mouth_color
        studio_mii["mouth_size"] = orig_mii.mouth_size
        studio_mii["mouth_type"] = orig_mii.mouth_type
        studio_mii["mouth_vertical"] = orig_mii.mouth_vertical
        studio_mii["beard_size"] = orig_mii.facial_hair_size
        studio_mii["beard_mustache"] = orig_mii.facial_hair_mustache
        studio_mii["beard_vertical"] = orig_mii.facial_hair_vertical
        studio_mii["nose_size"] = orig_mii.nose_size
        studio_mii["nose_type"] = orig_mii.nose_type
        studio_mii["nose_vertical"] = orig_mii.nose_vertical

        favorite_colors = {
            0: "Red",
            1: "Orange",
            2: "Yellow",
            3: "Lime Green",
            4: "Forest Green",
            5: "Royal Blue",
            6: "Sky Blue",
            7: "Pink",
            8: "Purple",
            9: "Brown",
            10: "White",
            11: "Black",
        }

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

        mii_studio = b"".join(hexlify(u8(m)) for m in mii_dict).decode("utf-8")

        stdout.buffer.write(b"Content-Type:application/json\n\n")
        stdout.flush()
        stdout.buffer.write(
            dumps(
                {
                    "mii": mii_data.decode("utf-8"),
                    "miistudio": mii_studio,
                    "name": orig_mii.mii_name,
                    "creator_name": orig_mii.creator_name,
                    "birthday": str(orig_mii.birth_month).zfill(2)
                    + "/"
                    + str(orig_mii.birth_day).zfill(2),
                    "favorite_color": favorite_colors[orig_mii.favorite_color],
                    "height": orig_mii.body_height,
                    "build": orig_mii.body_weight,
                    "gender": "Male" if orig_mii.gender == 0 else "Female",
                    "mingle": "N/A" if "switch" in input_type else "Yes" if orig_mii.mingle == 1 else "No",
                    "copying": "N/A" if "switch" in input_type or "wii" in input_type else "Yes" if orig_mii.copying == 1 else "No",
                }
            ).encode("utf-8")
        )

    elif input_type == "studio":
        mii_data = b""
        n = r = 256
        mii_dict = []
        for i in range(0, len(hexlify(input_data)), 2):
            mii_dict.append(int(hexlify(input_data)[i : i + 2], 16))
        mii_data += hexlify(u8(0))
        for v in mii_dict:
            eo = (
                7 + (v ^ n)
            ) % 256  # encode the Mii, Nintendo seemed to have randomized the encoding using Math.random() in JS, but we removed randomizing
            n = eo
            mii_data += hexlify(u8(eo))

        mii_studio = b"".join(hexlify(u8(m)) for m in mii_dict).decode("utf-8")

        stdout.buffer.write(b"Content-Type:application/json\n\n")
        stdout.flush()
        stdout.buffer.write(
            dumps(
                {
                    "mii": mii_data.decode("utf-8"),
                    "miistudio": mii_studio,
                }
            ).encode("utf-8")
        )

except:
    raise
    stdout.buffer.write(b"Content-Type:application/json\n\n")
    stdout.flush()
    stdout.buffer.write(
        dumps(
            {
                "mii": "000f165d65747981878c8e94a3a8b4acb3b7bec5cbd2dfe6f5f8fffc040b1c232b313f3a405a60697178808f9198a4",
                "studio": "Error!",
            }
        ).encode("utf-8")
    )
