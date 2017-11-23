# enigma2-ondemand-to-iptv-extension
uses various modules to generate IPTV bouquets of all programs listed from various on-demand services.

This essentially produces a bouquet.tv file which can be used on enigma2 boxes to have a full list of iplayer programs show as channels. 

Currently has an iPlayer Module for Enigma2 bouquets

You should first extract these files to a good location such as the default /opt/ondemand

open settings and change the cronkey to something unique (stops other people running your crons)

running main.py starts a web server which can handle simple requests. 

for example. Running 

http://serveripaddress/iplayer/cron/uniquecronid

will run the module iplayer, it uses get_iplayer (https://github.com/get-iplayer/get_iplayer)

**NOTE**
this must be installed and running in /usr/bin (only the main get_iplayer script is needed)

follow the instructions for get_iplayer to install the required perl modules to make it work (test by running get_iplayer once installed)

this cron will take a long time, the first time it's run. It will firstly download all programs on the iplayer today, save them into a small database, it will begins to loop through using get_iplayer to get the streaming ID and meta data and saves that to the database.

This can take a couple of hours the first time. 

When you run again, any entries with streaming URL's already are ignored and only new programs will have their streaming URL's downloaded. I'd recomended setting a cron to run this once an hour or two. 

Finally...

running http://serveripaddress/iplayer/bouquet will run through the database and generate an enigma2 bouquet of all programs. The file is cached and only regenerated when the cron has run and creates new entries. 

STILL TO DO....

i've rushed to build this in my spare time so bear with me while i polish it all. plus i'm not a python dev, this is the first time i've written anything in python. 

---Create a service for getting epg... maybe make it work as a source for crossepg or something
---Create a service to get a ZIP os all the meta images (will need cron to download these which will make the process even longer first time) this can then be named in a way to use as PICONS 
--Create a service to list all available moduels on the server
---Write an additional enigma2 plugin which can take a server address, list the modules and allow users to choose what they want / have it download bouquets, picons and epg automaticly based on an interval. 
--provide options in the bouquet service to filter, remove kids channels, news channels, etc. probably need a service showing module filter options and then have this show in the plugin automaticly based on the given server address.
--Write module for ITV hub
--wrtie module for UKTV play
--Write module for others...








