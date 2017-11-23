class odmodule():

	settings = None

	def __init__(self,od):

		#####################################################################
		##What is this Module Called? must also be the file name minus PY####
		#####################################################################

                self.moduleName = "iplayer"
		self.moduleTitle = "BBC iPlayer"
		self.moduleAuthor = "Louis Varley"
		self.moduleVersion = "2.1"

		###Carry These from the Main OD Classes to use
		self.od = od
		self.settings = self.od.appSettings();
		self.dbWriter = self.od.dbWriter(od)
		self.rawLocation = self.settings.tmpPath+self.moduleName+".raw"
		self.bouquetLocation = self.settings.tmpPath+self.moduleName+".tv"

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
	
                with file(self.rawLocation) as b:
                        l = b.readlines()
                        for line in l:
				lineCur=lineCur+1


                                if line[0].isdigit():

					
					index=line.split(":")[0]
                                        line=line.split(":",1)[1]
                                        title=line.split(",")[0].replace("      ","")

                                        print "##############################################"
                                        print "####        " + str(linecount-lineCur) + " LINES TO PROCESS INDEX " + index
                                        print "##############################################"
                                        print "\r"
					
                                        channel=line.split(",")[1]
                                        pid=line.split(",")[2]
					db.insertRow(pid,channel,title,self.moduleName,"","","","",index)
			
					if db.hasStreamURL(pid) is False:
						stream = self.fetchStreamURL(index)
						if stream is not None:
							db.updateStreamingURL(pid,stream[0],stream[1])

                                        if db.hasMeta(pid) is False:
                                                meta = self.fetchMeta(index)
                                                if meta is not None:
                                                        db.updateMeta(pid,meta[0],meta[1])

			##############################################################################
			##Call this finally, otherwise the main class will never regenerate a bouquet#
                        ##############################################################################
			os.remove(self.bouquetLocation)

	
	def fetchMeta(self,index):

		import subprocess

                #Extract Streaming URL
                stdout = subprocess.check_output(["get_iplayer", "--info",index], stderr=subprocess.STDOUT)

                #clean list
                lines = stdout.splitlines()
                num=0
                ext=""
                cleanedLines = lines
                newLines=[]

                keeps = ['desc:','thumbnail:']

                for line in lines:
                    if any(keep in line for keep in keeps):
                          newLines.append(line)

                for line in newLines:

                        if line[:5] == "desc:":

                                desc = newLines[num].split(":",1)[1].replace("  ","")
                                thumbnail = newLines[num+1].split(":",1)[1].replace(" ","")

                        num=num+1

                if desc is None:
                        return ['!','!']
                else:
                        return [desc,thumbnail]



