#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from classes.tinydb import TinyDB, Query
from SocketServer     import ThreadingMixIn

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
		server_class=self.ThreadedHTTPServer
    		server_address = ('', port)
    		httpd = server_class(server_address, self.www)
    		print 'Starting ondemand httpd...'
    		httpd.serve_forever()

        def logthis(self,logln):
                with open(self.settings.logFile, "a") as logfile:
                     now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                     logfile.write(str(now) + ":" + str(logln) + "\n")

	def listModules(self):
		print "bla"

	def getModuleInfo(self,module):
		mod = importlib.import_module('modules.'+module)
                odmClass = getattr(mod,'odmodule')
                odm = odmClass(self.od)
                info = odm.moduleInfo()
                return info


	def getModuleTitle(self,module):
		mod = importlib.import_module('modules.'+module)
                odmClass = getattr(mod,'odmodule')
                odm = odmClass(self.od)
                title = odm.moduleTitle
		return title

	def generateIndex(self,od,module):
		db = od.dbWriter(od)
		results = db.getIndex(module)
		line=""
		for result in results:
			if result['id'] is not None:
				line=line+result['id']+'\n'

		settings = od.appSettings()

		with open(settings.indexPath+module+".index","w") as index:
			index.write(line)

        def getModules(self):

		s = self.appSettings()

		modules={}

                ##Loops all Available Modules.
                for filename in os.listdir("./modules"):
                    if filename.endswith(self.module + ".py") and "init" not in filename:
                    	p, m = filename.rsplit('.', 1)
			print m
			

			


	
	##DB Writer Class
	class dbWriter():

		def __init__(self,od):
			self.settings = od.appSettings()
			self.db = TinyDB(self.settings.dbPath)

		#Purge everything in DB
		def purgeAll(self):
			self.db.purge()
			self.db.all()


		##Find a show for a module matching an ID
		def getByID(self,id,module):
			
			rows = Query()
                        results = self.db.search((rows.id == id) & (rows.module == module) )
                        if results:
				return results
                        else:

                                return None


		#If Row does not excist, create, if it does update
		def insertUpdateRow(self,id,channel,title,module,url,expires,thumbnail,description):
			rows = Query()
			results = self.db.search(rows.id == id)
			if not results:
				self.db.insert({'id': id, 'channel': channel, 'title': title, 'module': module, 'url': url, 'expires': expires, 'thumbnail': thumbnail, 'description': description })
			else:

				self.db.update({'description': description, 'thubmnail': thumbnail, 'url': url, 'expires': expires, 'title': title, 'channel': channel},(rows.id == id) & (rows.module == module))

		def getIndex(self,module):
                        rows = Query()
                        results = self.db.search(rows.module == module)
                        return results

		def getListings(self,module):
			
			rows = Query()
			results = self.db.search((rows.module == module) & (rows.url != "None" ) & (rows.url != "!") & (rows.title != "None") & (rows.url != ""))
			return results

        	def deleteRowByID(self,module,id):
        	        rows = Query()
        	        #self.db.remove(rows.id == id AND rows.module == module)

	##########################################################################
        ##Class for a show / stream
        ##########################################################################
	
	class show():

		def __init__(self,od):

			self.od = od
			self.id = None
			self.title = None
			self.url = None
			self.expires = None
			self.thumbnail = None
			self.description = None
			self.channel = None
			self.module = None

		def load(self,id,module):

			db = self.od.dbWriter(od)

			foundShow = db.getByID(id,module)

			if foundShow is not None:
				self.id = foundShow[0]['id']
				self.title = foundShow[0]['title']
				self.url = foundShow[0]['url']
				self.expires = foundShow[0]['expires']
				self.thumbnail = foundShow[0]['thumbnail']
				self.description = foundShow[0]['description']
				self.channel = foundShow[0]['channel']
				self.module = foundShow[0]['module']

		def updateCreate(self):

			db = self.od.dbWriter(od)
			db.insertUpdateRow(self.id,self.channel,self.title,self.module,self.url,self.expires,self.thumbnail,self.description)				
			

	##########################################################################
	##Class for Holding any App Settings
        ##########################################################################

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
			self.indexPath = config.get('settings','indexPath')

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

					#Index file used to create a quick list of ID's for this module
					if os.path.isfile(s.indexPath+p+'.index'):
		                                os.remove(s.indexPath+p+'.index')
					self.od.generateIndex(self.od,p)
					odm.autorun()

	class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    		pass

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
                                self.thisCronKey = "none"


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
				self._set_headers()
				filters = self.getParamsAsDict(self.path)
				self.wfile.write(bouquet.generateBouquet(self.thisModule,filters))
			
			elif self.thisAction == "epg":
				print "Generate EPG"

			elif self.thisAction == "picons":
				print "Generate Picon"	

			elif self.thisAction == "info":
				self._set_headers()
				self.wfile.write(od.getModuleInfo(self.thisModule))

			else:
				self._set_headers()
				self.wfile.write("Invalid Request")



   		def do_HEAD(self):
        		self._set_headers()

		def getParamsAsDict(self,url):
			if "?" in url:
 				qs = url.split("?")[1]
				final_dict = dict()
 		   		for item in qs.split("&"):
        				final_dict[item.split("=")[0]] = item.split("=")[1]
    				return final_dict
			else:
				return None






	class bouquet():
		
		def __init__(self,od):
			self.od = od
	
		##Generates Bouquet for the given moduel and returns
		def generateBouquet(self,module,filter):

			import os

                        settings = od.appSettings()
                        moduleBouquet = settings.tmpPath + module + '.tv'
			
			#If Bouquet already generated use that
			if not os.path.isfile(moduleBouquet):
	
				line = ""
				line = line + "#NAME " + od.getModuleTitle(module) + "\n"
				db = od.dbWriter(od)
				rows = db.getListings(module)
	
				for row in rows:
						if row['title'] is not None and row['channel'] is not None and row['url'] is not None:
							line = line + self.bouquetLine(row['title'].strip() + " [" + row['channel'].strip() +  "]",row['url']) + "\n"
				
				thisBouquet = open(moduleBouquet, 'w')
				thisBouquet.write(line)
				thisBouquet.close()

			returnln = ""

			with open(moduleBouquet) as thisBouquet:
				thisBouquetContent = thisBouquet.readlines()
                        	for bouquetLine in thisBouquetContent:
					
					try:
						exclude=filter['exclude']

						if not any(line in bouquetLine.lower() for line in filter['exclude'].lower().split(",")):

							returnln = returnln + bouquetLine

					except:

							returnln = returnln + bouquetLine 

				return returnln

		##Generates an Enigma2 Bouquet Line
		def bouquetLine(self,title,url):
			if url is not None and title is not None:
				return "#SERVICE 4097:0:1:1:0:0:0:0:0:3:"+urllib.quote(url)+":"+title.replace("  ","")
			else:
				print "none"

##########################################################################################

##Setup and Begin the Auto Run Service

def autorunThread(od):

	autorunService = od.autorun(od)
	autorunService.run()


def webThread(od):

	od.runWeb(od)

od = onDemand()

webThread(od)
