##od module class is a module for the main od service
##You must provide the following...

##1) an init() which setups up as minimum the name,title,author and version
##2) an autorun() which will be called by cron, this needs to download, organise and save to the db the program listings
##3) an moduleInfo() which will provide some details about this plugin in json format which can be sent to any plugins calling it,
##	include, module,title,filters

class odmodule():

	settings = None

	def __init__(self,od):

		#####################################################################
		##What is this Module Called? must also be the file name minus PY####
		#####################################################################

                self.moduleName = "itv-hub"
		self.moduleTitle = "ITV Hub"
		self.moduleAuthor = "Louis Varley"
		self.moduleVersion = "1.1"
		self.moduleFilters = [
			{'title':'Exclude CITV','keyword':'citv'},
                        {'title':'Weather','keyword':'weather'},
                        {'title':'News','keyword':'news'}
		]

		###Carry These from the Main OD Classes to use
		self.od = od
		self.settings = self.od.appSettings();
		self.dbWriter = self.od.dbWriter(od)
		self.rawLocation = self.settings.tmpPath+self.moduleName+".raw"
		self.bouquetLocation = self.settings.tmpPath+self.moduleName+".tv"

	##This will be called when the OD service is run calling for a list of filters to be available, in any plugins eventually.
	##It should return a json string listing what keywords this plugin can filter 
	
	def moduleInfo(self):

		info={
			'filters':self.moduleFilters,
                        'author':self.moduleAuthor,
                        'version':self.moduleVersion,
                        'title':self.moduleTitle,
                        'name':self.moduleName,
		}

		return info


	#############################################################################################################################
        ##Autorun is called by cron, it should essentially do the work filling the database using the carried over dbWriter class####
        #############################################################################################################################

	def autorun(self):

		#####################################################
		##Edit This Part to work with your ondemand service##
		#####################################################

		import os
		import urllib

		print "Running " + self.moduleTitle + " module - " + self.moduleAuthor + " v" + self.moduleVersion

		##Create Raw output from get_iplayer
                os.system("get_iplayer > "+self.rawLocation)

		db = self.dbWriter

		##Debug for testing, clear database and redownload everything
		#db.purgeAll()

		lineCur=0
		linecount = sum(1 for line in open(self.rawLocation))

		##Read the raw file and add to the db
	
                with file(self.rawLocation) as b:
                        l = b.readlines()
                        for line in l:

				lineCur=lineCur+1
                                if line[0].isdigit():

                                        print "##############################################"
                                        print "####        " + str(linecount-lineCur) + " LINES TO PROCESS, CURRENTLY ON " + str(lineCur)
                                        print "##############################################"
                                        print "\r"

					index=line.split(":")[0] ##Line Number
                                        line=line.split(":",1)[1]
                                        title=line.split(",")[0].replace("      ","").lstrip().rstrip() ##Show Title
                                        channel=line.split(",")[1].lstrip()
                                        pid=line.split(",")[2].strip()

					thisShow = None
					thisShow = self.od.show(self.od)
					
					##Check if this show is indexed
					thisShow.load(pid,self.moduleName)
					
					if(thisShow.id is None):
					##This is a new show so add the ID and title
						print "Adding new Show [" + title + "..."
                                                thisShow.id = pid
                                                thisShow.title = title
						thisShow.channel = channel
						newShow=True

					else:
						newShow=False
						print "Existing show..."
	
					if thisShow.url is None and newShow == True:
						print "Updating Stream..."
						stream = self.fetchStreamURL(pid)
						thisShow.url = stream['url']
						thisShow.expires = stream['expires']


					if thisShow.description is None and newShow == True:
						print "Updating Thumbnail..."
						meta = self.fetchMeta(pid)
						thisShow.thumbnail = meta['thumbnail']
						thisShow.description = meta['description']

					thisShow.module = self.moduleName

					thisShow.updateCreate()


			##############################################################################
			##Call this finally, otherwise the main class will never regenerate a bouquet#
                        ##############################################################################
			os.remove(self.bouquetLocation)


	##Extracts the Streaming URL's using the PID from get iplayer and finds the one which is an MP4 with the highiest priority
        def fetchStreamURL(self,pid):

                import subprocess

                #Extract Streaming URL
                stdout = subprocess.check_output(["get_iplayer", "--streaminfo","pid:"+pid.strip()], stderr=subprocess.STDOUT)

                #clean list
                lines = stdout.splitlines()
                num=0
                ext=""
		hPriority=0
                cleanedLines = lines
                newLines=[]
		url=None

                keeps = ['expires:','priority:','streamurl:','ext:']

                for line in lines:
                    if any(keep in line for keep in keeps):
                          newLines.append(line)

                for line in newLines:

                        if line[:8] == "expires:":

                                expires = newLines[num].split(":",1)[1].replace(" ","")
                                ext = newLines[num+1].split(":",1)[1].replace(" ","")
                                priority = newLines[num+2].split(":",1)[1].replace(" ","")
                                streamurl = newLines[num+3].split(":",1)[1].replace(" ","")

                        num=num+1

			if priority > hPriority and ext == 'mp4':

				hPriority = priority
				url = streamurl

                if url is None:
			print "No Streaming URL Found"
                        return {'url': None,'expires': None}
                else:
                        return {'url': url,'expires': expires}


	##Fetch meta for the given PID
	def fetchMeta(self,pid):

		import subprocess

                #Extract Streaming URL
                stdout = subprocess.check_output(["get_iplayer", "--info","pid:"+pid.strip()], stderr=subprocess.STDOUT)

                #clean list
                lines = stdout.splitlines()
                num=0
                cleanedLines = lines
                newLines=[]
		description=None
		thumbnail=None

                keeps = ['desc:','thumbnail:']

                for line in lines:
                    if any(keep in line for keep in keeps):
                          newLines.append(line)

                for line in newLines:

                        if line[:5] == "desc:":

                                description = newLines[num].split(":",1)[1].replace("  ","")
                                thumbnail = newLines[num+1].split(":",1)[1].replace(" ","")

                        num=num+1

                if description is None:
                        return {'description': None,'thumbnail': None}
                else:
                        return {'description': description,'thumbnail': thumbnail}


		



