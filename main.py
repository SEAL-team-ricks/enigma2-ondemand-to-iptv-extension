#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from classes.tinydb import TinyDB, Query

import urlparse
import datetime
import os.path
import importlib
import json
import urllib
import urlparse

from pydoc import locate

#################################################################################
### OnDemand Main Class
#################################################################################

class onDemand():

	od = None
	
	def __init__(self):
		self.settings = self.appSettings()
		self.od = self

	def runWeb(self,od):
		port=80
		server_class=HTTPServer
    		server_address = ('', port)
    		httpd = server_class(server_address, self.www)
    		print 'Starting ondemand httpd...'
    		httpd.serve_forever()

        def logthis(self,logln):
                with open(self.settings.logFile, "a") as logfile:
                     now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                     logfile.write(str(now) + ":" + str(logln) + "\n")

	##DB Writer Class
	class dbWriter():

		def __init__(self,od):
			self.settings = od.appSettings()
			self.db = TinyDB(self.settings.dbPath)

		#Purge everything in DB
		def purgeAll(self):
			self.db.purge()
			self.db.all()

		#Does this entry have a URL stream
		def hasStreamURL(self,id):
		        
			rows = Query()
                        results = self.db.search((rows.id == id ) & (rows.url == "None"))
			if results:
				print "Missing streaming URL"
				return False
			else:

				return True

                #Does this entry have a URL stream
                def hasMeta(self,id):

                        rows = Query()
                        results = self.db.search((rows.id == id ) & (rows.description == "None"))
                        if results:
                                print "Missing Meta"
                                return False
                        else:

                                return True


		#If Row does not excist, create, if it does check the index is still the same and otherwise update
		def insertRow(self,id,channel,title,module,url,expires,thumbnail_url,description,index):

			print "Processing " + title.replace("  ","")

			rows = Query()
			results = self.db.search(rows.id == id)
			if not results:
				self.db.insert({'id': id, 'channel': channel, 'title': title, 'module': module, 'url': 'None', 'expires': 'None', 'thumbnail': 'None', 'description': 'None', 'index': index })
				print "Inserted new Record"
			else:

				results = self.db.search((rows.id == id) & (rows.index == index))
	
				if not results:
					print "Index Updated"
					self.db.update({'index': index}, (rows.id == id) & (rows.index == index))
				else:

					print "Skipped Record"

		def updateStreamingURL(self,id,url,expires):
			rows = Query()
			self.db.update({'url': url, 'expires': expires},rows.id == id)	
			print "Added Streaming URL"		

                def updateMeta(self,id,description,thumbnail):
                        rows = Query()
                        self.db.update({'description': description, 'thubmnail': thumbnail},rows.id == id)
                        print "Updated Meta"

		def getListings(self,module):
			rows = Query()
			results = self.db.search((rows.module == module) & (rows.url != "None" ) & (rows.url != "!"))
			return results

		##Update the URL and the Expires using the Module and ID
        	def updateRowByID(self,module,id,url,expires):
			rows = Query()
        	        #self.db.update({'channel': channel, 'title': title, 'url': url, 'expires', expires },rows.id == id AND rows.module == module)

        	def deleteRowByID(self,module,id):
        	        rows = Query()
        	        #self.db.remove(rows.id == id AND rows.module == module)


	##Class for Holding any settings
	class appSettings():


		def __init__(self):

			import ConfigParser
			config = ConfigParser.ConfigParser()
			config.read("settings")

			self.serverBlackList = config.get('settings','blackListFile')
			self.odPath = config.get('settings','odPath')
			self.tmpPath = config.get('settings','tmpPath')
			self.logFile = config.get('settings','logFile')
			self.dbPath = config.get('settings','dbFile')
			self.cronKey = config.get('settings','cronUniqueKey')

	##Class which runs all other modules, once started auto run will loop every X seconds
	class autorun():
	
		def __init__(self,od,module):
			self.od = od
			self.module = module
			self.settings = od.appSettings()

		def run(self):

			s = self.settings

			##Loops all Available Modules. 
			print "Service Starting"
			for filename in os.listdir("./modules"):
    				if filename.endswith(self.module + ".py") and "init" not in filename: 			
               				p, m = filename.rsplit('.', 1)
                			mod = importlib.import_module('modules.'+p)
                			odmClass = getattr(mod,'odmodule')
                			odm = odmClass(self.od)
					odm.autorun()

	##Class which runs webserver and handles http requests for bouquets, epg and picons
	class www(BaseHTTPRequestHandler):
		
		global od

   		def _set_headers(self):
        		self.send_response(200)
       	 		self.send_header('Content-type', 'text/html')
        		self.end_headers()

    		def _set_error(self):
        		self.send_response(401)
        		self.end_headers()

    		def _set_redirect(self,URL):
        		self.send_response(301)
        		self.send_header('Location',URL)
        		self.end_headers()

    		def getParam(self,param):
			if param + "=" in self.path: 
				return urlparse.parse_qs(urlparse.urlparse(self.path).query)[param][0]
			else:
				return "false"

    		def do_GET(self):

			settings = od.appSettings()

			#Clients IP Address
        		clientIP = self.client_address[0]

			#If Client IP Is Blocked in Blacklist file, log and drop
			if clientIP in open(settings.serverBlackList).read():
    				print("blocked")
	                        od.logthis(clientIP + ":" + "Blocked By Blacklist")
				self._set_error()
				return False

			self.thisCronKey="None"
			self.thisModule="None"
			self.thisAction="None"

			try:
				self.thisModule = self.path.split("/")[1]
			except IndexError:
				self.thisAction = "none"

			try:
				self.thisAction = self.path.split("/")[2]
			except IndexError:
				self.thisAction = "none"

			try:
                                self.thisCronKey = self.path.split("/")[3]
			except IndexError:
                                self.thisAction = "none"


			#Log Action
			od.logthis(clientIP + ":" + str(self.thisModule) + ":" + str(self.thisAction))

			if self.thisAction == "cron" and self.thisCronKey == settings.cronKey:
				self._set_headers()
				self.wfile.write("Running Cron for " + self.thisModule)
				autorunService = od.autorun(od,self.thisModule)				
	                        od.logthis(clientIP + ": Cron started for " + str(self.thisModule))
				autorunService.run()
	                        od.logthis(clientIP + ": Cron finished for " + str(self.thisModule))
				return


			if self.thisAction == "bouquet":
				bouquet = od.bouquet(self.thisModule)
				self.wfile.write(bouquet.generateBouquet(self.thisModule))
				return
			
			if self.thisAction == "epg":
				print "Generate EPG"
				return

			if self.thisAction == "picons":
				print "Generate Picon"	
				return

			self._set_headers()
			self.wfile.write("Invalid Request")



   		def do_HEAD(self):
        		self._set_headers()

	class bouquet():
		
		def __init__(self,od):
			self.od = od
	
		##Generates Bouquet for the given moduel and returns
		def generateBouquet(self,module):

			import os

                        settings = od.appSettings()
                        moduleBouquet = settings.tmpPath + module + '.tv'
			
			#If Bouquet already generated use that
			if not os.path.isfile(moduleBouquet):
	
				line = ""
				line = line + "#NAME " + module + "\n"
				db = od.dbWriter(od)
				rows = db.getListings(module)
				for row in rows:
					line = line + self.bouquetLine(row['title'],row['url']) + "\n"
				
				thisBouquet = open(moduleBouquet, 'w')
				thisBouquet.write(line)
				thisBouquet.close()

			with open(moduleBouquet) as thisBouquet:
				thisBouquetContent = thisBouquet.read()
                        	return thisBouquetContent




		##Generates an Enigma2 Bouquet Line
		def bouquetLine(self,title,url):
			return "#SERVICE 4097:0:1:1:0:0:0:0:0:3:"+urllib.quote(url)+":"+title.replace("  ","")

##########################################################################################

##Setup and Begin the Auto Run Service

def autorunThread(od):

	autorunService = od.autorun(od)
	autorunService.run()


def webThread(od):

	od.runWeb(od)

od = onDemand()

webThread(od)
