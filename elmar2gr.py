# Name:    elmar2gr /main
# Author:  Ludger A. Rinsche
# Release: 30.09.2010
''' This file is part of elmar2gr.

    elmar2gr is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    elmar2gr is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with elmar2gr. If not, see <http://www.gnu.org/licenses/>.
'''


import mainloops as mainloops
import helper    as listen
import string    as string
import traceback as traceback
import codecs    as codecs
import settings  as settings
import os
import gzip
import shutil

if not os.path.isdir(settings.outputdir+os.sep):
    os.makedirs(settings.outputdir+os.sep)
    
print
print "------------------------------------------------------------------"
print

listfile  = open(settings.listfile, "r")
errorfile = open(settings.errorfile, "a")
main_sitemap_file = codecs.open(settings.outputdir + os.sep + "sitemap.xml", "w+", "utf8", errors="ignore")
main_sitemap_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n")
errorcount=0
i=0
l=0

ang = 0
ges = 0

for each in listfile:
    errorEX = "Nein."
    i+=1
    
    if ((i>=settings.startat and i<=settings.endwith) or (settings.endwith+settings.startat==0)):
        l+=1

        try:
            shop = mainloops.ShopDaten()
            shop.paramenter.Scurrency  = settings.Scurrency
            shop.paramenter.Slanguage  = settings.Slanguage
            shop.paramenter.Snamespace = settings.Snamespace
            shop.paramenter.Sbaseuri   = settings.Sbaseuri
            shop.paramenter.outputdir  = settings.outputdir
            shop.paramenter.timeout    = settings.timeout
            shop.paramenter.ypfapikey  = settings.ypfapikey
            shop.paramenter.usepos     = settings.usepos
            ang = 0
            this_url =""
            this_name=""
            this_folder=""
            
            ang, this_url, this_name, this_folder = shop.convert(each.strip())
            ges = ges + ang
            
        except Exception, e:
            errorEX=str(e)
            print >> errorfile, str(i)+"; "+each.strip()+"; "+str(e)
        
        print str(i).rjust(4,' ') + ": " + this_folder + " | Fehler?: " + errorEX + " | Angelegte Produkte: " + str(ang)
        if ((errorEX=="Nein.") and (ang>0)):
            this_name = listen.clearchars(this_name, 50, True)
            
            if not os.path.isdir(settings.outputdir+os.sep+this_folder+os.sep+"data"+os.sep):
                os.makedirs(settings.outputdir+os.sep+this_folder+os.sep+"data"+os.sep)
                
            f_in = open(settings.outputdir + os.sep + this_folder + os.sep + "rdf" + os.sep + "products.rdf", "rb")
            gz_file = gzip.open(settings.outputdir + os.sep + this_folder + os.sep + "data" + os.sep + "products.rdf" + ".gz", "wb")
            gz_file.writelines(f_in)
            gz_file.close()
            f_in.close()

            f_in = open(settings.outputdir + os.sep + this_folder + os.sep + "rdf" + os.sep + "shop.rdf", "rb")
            gz_file = gzip.open(settings.outputdir + os.sep + this_folder + os.sep + "data" + os.sep + "shop.rdf" + ".gz", "wb")
            gz_file.writelines(f_in)
            gz_file.close()
            f_in.close()
            
            sitemap_file = codecs.open(settings.outputdir + os.sep + this_folder + os.sep + "sitemap.xml", "w+", "utf8", errors="ignore")
            sitemap_file.write(listen.createSingleSitemap(this_name, settings.Sbaseuri, this_folder, settings.sitechangefreq))
            sitemap_file.close()
            main_sitemap_file.write(listen.createPartMainSitemap(settings.Sbaseuri,this_folder))
            
        else:
            #print this_folder
            errorcount+=1
            print str(traceback.format_exc())
            print
            
            if ((os.path.isdir(settings.outputdir+os.sep+this_folder+os.sep)) and (this_folder!="")):
                try:
                    print "Trying to delete "+settings.outputdir+os.sep+this_folder+os.sep
                    shutil.rmtree(settings.outputdir+os.sep+this_folder+os.sep)
                except Exception, e:
                    print "Error while deleting useless dir."

    if ((i>=settings.endwith) and (settings.endwith+settings.startat!=0)): break


print "------------------------------------------------------------------"
print " DONE: Anzahl: " + str(l).rjust(4,' ') + "  Fehler: " + str(errorcount).rjust(4,' ') + " Produkte: "+str(ges)

main_sitemap_file.write("</sitemapindex>\n")
main_sitemap_file.close()
listfile.close()
errorfile.close()