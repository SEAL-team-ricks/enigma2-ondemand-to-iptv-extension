#!bin/bash

yourserver="my.ip.address"

wget "http://${yourserver}/iplayer/bouquet/?exclude=cbbc,s4c,alba,cbeebies,news,parliament,football" -O iplayer.tmp

bouquetLine="#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.ondemand.iplayer.feeds.main.tv\" ORDER BY bouquet"

grep -q -F "$bouquetLine" /etc/enigma2/bouquets.tv || echo $bouquetLine >> /etc/enigma2/bouquets.tv

echo "Creating Bouquet File"

mv iplayer.tmp /etc/enigma2/userbouquet.ondemand.iplayer.feeds.main.tv

echo "Reload Bouquets"

wget -qO - "http://127.0.0.1/web/servicelistreload?mode=2"
wget -qO - "http://127.0.0.1/web/servicelistreload?mode=2"


