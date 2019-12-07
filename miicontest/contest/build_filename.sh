cp $1.dec $1.ces1
lzss -evf $1.ces1
openssl enc -aes-128-cbc -e -in $1.ces1 -out $1.ces2 -K 8D22A3D808D5D072027436B6303C5B50 -iv BE5E548925ACDD3CD5342E08FB8ABFEC
openssl dgst -sha1 -mac HMAC -macopt hexkey:4CC08FA141DE2537AAA52B8DACD9B56335AFE467 -binary -out $1.ces4 $1.ces2
cat 4bytes.bin $1.ces4 $1.ces2 > $1.ces
