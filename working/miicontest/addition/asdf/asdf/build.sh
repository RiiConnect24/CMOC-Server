cp con_info.dec con_info.ces1
/var/rc24/File-Maker/Tools/LZ\ Tools/lzss/lzss -evf con_info.ces1
openssl enc -aes-128-cbc -e -in con_info.ces1 -out con_info.ces2 -K 8D22A3D808D5D072027436B6303C5B50 -iv BE5E548925ACDD3CD5342E08FB8ABFEC
openssl dgst -sha1 -mac HMAC -macopt hexkey:4CC08FA141DE2537AAA52B8DACD9B56335AFE467 -binary -out con_info.ces4 con_info.ces2
cat con_info.ces3 con_info.ces4 con_info.ces2 > con_info.ces
