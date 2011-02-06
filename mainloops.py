# Name:    elmar2gr /mainloops
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

import xml.dom.minidom as dom
import codecs  as codecs
import helper  as listen
import csv     as csv
import string  as string
import urllib2 as urllib
import os

class ShopDaten(object):
    class Parameters(object):
        def __init__(self):
            self.Scurrency ="EUR"
            self.Slanguage ="DE"
            self.Snamespace="http://www.123-testshop.tld/"
            self.Sbaseuri  ="http://www.123-testshop.tld/"
            self.outputdir ="output"
            self.ypfapikey =""
            self.usepos    =False
        
    class ShopUpdate(object):
        def __init__(self):
            self.method  =False
            self.spalten ={}
            self.url     =""
            self.tag     =""
            self.ab      =""
            self.bis     =""
            self.delimiter=""
            self.escaped  =""
            self.quoted   =""
            self.lineend  =""
    
    class PayStuff(object):
        def __init__(self):
            self.name     =""
            self.type     =""
            self.kostenEX =False
            self.kosten   =""
            self.maxkosEX =False
            self.maxkosten=""
            self.kocurr   =""
            self.maxkocurr=""       
    
    class SpecialOfferStuff(object):
        def __init__(self):
            self.type   = ""
            self.unfree = True

    class ForwardExpensesStuff(object):
        def __init__(self):
            self.FlatrEx = False
            self.BoundEx = False
            self.FlatrCu = ""
            self.BoundCu = ""
            self.FlatrVa = ""
            self.BoundVa = ""    
    
    class ShopAdress(object):
        def __init__(self):
            self.sale    =False
            self.exists  =False
            self.hasgeo  =False
            self.compname=""
            self.street  =""
            self.postcode=""
            self.city    =""
    
    class PhoneStuff(object):
        def __init__(self):
            self.exists  =False
            self.number  =""
            self.costspm =""
            self.costspc =""
            self.currency=""
  
    def __init__(self):
        self.updateM     =self.ShopUpdate()
        self.shopinfourl =""
        self.foldername  =""
        self.clearedname =""   
        self.currency    =""
        self.language    =""
        self.name        =""
        self.description =""
        self.urlseealso  =""
        self.urllogo     =""
        self.publicemail =""
        self.privatemail =""
        self.paramenter  =self.Parameters()
        self.adress1     =self.ShopAdress()
        self.adress2     =self.ShopAdress()
        self.orderphone  =self.PhoneStuff()
        self.orderfax    =self.PhoneStuff()
        self.hotline     =self.PhoneStuff()
        self.forwardexp  =self.ForwardExpensesStuff()
        self.produktecnt = 0
        self.specoffers  = []
        self.produkte    = []                           # In diese Liste werden die einzelnen Zeilen der CSV-Datei gespeichert,
        self.herstdict   = {}                           # Schluessel wird der Name des Herstellers laut CSV-Datei, Wert der bereinigte, eindeutige Name.         
        self.paymethods  = []
        self.offeringnames=[]                           # In diese Liste werden die IDs der Offerings (normale und spezielle) eingetragen, damit nachtraeglich <gr:offers rdf:ressource...> erstellt werden kann.
        self.testfortitles=""                           # Wird benoetigt, um zu ueberpruefen, ob die erste Zeile eine Titelzeile ist.
        self.tmpShopMetaData = ""
        self.tmpProdMetaData = ""


    def convert(self, datei="input/test_shopinfo.xml"):
        self.shopinfourl=datei
        self.readShopXML(datei)
        self.readProdCSV()
        self.writeShopRDF()
        try:
            i = self.writeProdCSV()
        except Exception, e:
            print "Error in writeProdCSV."
            i = 0
                
        return(i, self.urlseealso, self.name, self.foldername)
        
    def readShopXML(self, dateiname="input/test_shopinfo.xml"):
        req = urllib.Request(url=dateiname, headers = { 'User-Agent' : 'elmar2goodrelations/1.0' })
        datei = urllib.urlopen(req, timeout=self.paramenter.timeout)
        content = datei.read()           
        baum = dom.parseString(content)
        
        #UpdateMechnismus
        updateBaum=baum.getElementsByTagName("UpdateMethods")
        if len(updateBaum)>0:
            for fetched in updateBaum[0].childNodes:
                if fetched.nodeName == "DirectDownload":
                    self.updateM.method = True
                    self.updateM.tag = fetched.getAttribute("day")
                    self.updateM.ab  = fetched.getAttribute("from")
                    self.updateM.bis = fetched.getAttribute("to")
                    
                    csvBaum = baum.getElementsByTagName("CSV")
                    if len(csvBaum)>0:
                        for fetched in csvBaum[0].childNodes:
                                if fetched.nodeName == "Header":
                                    self.testfortitles = str(fetched.firstChild.data)
                                if fetched.nodeName == "Url":
                                    self.updateM.url = str(fetched.firstChild.data)
                                if fetched.nodeName == "SpecialCharacters":
                                    self.updateM.delimiter= str(fetched.getAttribute("delimiter"))
                                    self.updateM.escaped  = str(fetched.getAttribute("escaped"))
                                    self.updateM.quoted   = str(fetched.getAttribute("quoted"))
                                    if self.updateM.quoted=="": self.updateM.quoted='"'
                                    self.updateM.lineend  = str(fetched.getAttribute("lineend"))
                                    if (self.updateM.delimiter==r"\t") or (self.updateM.delimiter=="[tab]") or (self.updateM.delimiter==r"[tab]"):
                                        self.updateM.delimiter="\t"

                    mapBaum = baum.getElementsByTagName("Mappings")
                    if len(mapBaum)>0:
                        for fetched in mapBaum[0].childNodes:
                                if fetched.nodeName == "Mapping":
                                    schl = fetched.getAttribute("type")
                                    wert = fetched.getAttribute("column")
                                    self.updateM.spalten.update({str(schl): int(wert)})    

            if self.updateM.method == False:
                return "DirectDownload wird nicht unterstuetzt! (1)"
        else:
            return "DirectDownload wird nicht unterstuetzt! (2)"
    
        # Common: Sprache und Waehrung
        commonBaum=baum.getElementsByTagName("Common")
        if len(commonBaum)>0:
            for fetched in commonBaum[0].childNodes:
                if fetched.nodeName == "Language":
                    if fetched.firstChild.data != None:
                        self.language=fetched.firstChild.data
                    else:
                        self.language=self.paramenter.Slanguage
                if fetched.nodeName == "Currency":
                    if fetched.firstChild.data != None:
                        self.currency=fetched.firstChild.data
                    else:
                        self.currency=self.paramenter.Scurrency
        
        #osp:Shop: Name, Shop-URL, Logo und Beschreibung
        ospShopBaum=baum.getElementsByTagName("osp:Shop")
        if len(ospShopBaum)>0:
            for fetched in ospShopBaum[0].childNodes:
                if fetched.nodeName == "Name":
                    self.name=listen.replace_XMLEntities(fetched.firstChild.data)
                    c=0
                    while c <> len(self.name) and c<25:
                        if (self.name[c] in string.letters) or (self.name[c] in string.digits):
                            self.clearedname=self.clearedname+self.name[c]
                        c+=1

                if fetched.nodeName == "Url" and (type(fetched.firstChild).__name__ != "NoneType"):
                    self.urlseealso=listen.replace_XMLEntities(fetched.firstChild.data)
                    self.foldername=listen.clearedurl(self.urlseealso)
                    if (self.foldername.endswith("/")):
                        self.foldername=self.foldername[:-1]
                    self.tmpShopMetaData = listen.createHttpMetaDat(datei.info(), self.paramenter, self.foldername, "shop")
    
                if fetched.nodeName == "Self-Description" and (type(fetched.firstChild).__name__ != "NoneType"):
                    self.description= listen.replace_XMLEntities(fetched.firstChild.data)
                if fetched.nodeName == "Logo" and (type(fetched.firstChild).__name__ != "NoneType"):
                    self.urllogo=listen.replace_XMLEntities(fetched.firstChild.data)
            
        #Contact: Private und Oeffentliche EMailadresse
        contactBaum=baum.getElementsByTagName("Contact")
        if len(contactBaum)>0:
            for fetched in contactBaum[0].childNodes:
                if fetched.nodeName == "PublicMailAddress":
                    self.publicemail=fetched.firstChild.data
                if fetched.nodeName == "PrivateMailAddress":
                    self.privatemail=fetched.firstChild.data
    
        #Adress: Verkauf, Strasse, PLZ und co.
        adressBaum=baum.getElementsByTagName("Address")
        if len(adressBaum)>0:
            self.adress1.exists = True
            self.adress1.sale = adressBaum[0].getAttribute("sale")
            for fetched in adressBaum[0].childNodes:
                if fetched.nodeName == "CompanyName":
                    self.adress1.compname = fetched.firstChild.data 
                if fetched.nodeName == "Street":
                    self.adress1.street      = fetched.firstChild.data
                if fetched.nodeName == "Postcode":
                    self.adress1.postcode    = fetched.firstChild.data
                if fetched.nodeName == "City":
                    self.adress1.city        = fetched.firstChild.data
                        
            if len(adressBaum)>1:
                self.adress2.exists = True
                self.adress2.sale = adressBaum[1].getAttribute("sale")
                for fetched in adressBaum[1].childNodes:
                    if fetched.nodeName == "CompanyName":
                        self.adress2.compname = fetched.firstChild.data
                    if fetched.nodeName == "Street":
                        self.adress2.street      = fetched.firstChild.data
                    if fetched.nodeName == "Postcode":
                        self.adress2.postcode    = fetched.firstChild.data
                    if fetched.nodeName == "City":
                        self.adress2.city        = fetched.firstChild.data    
    
        #OrderPhone: Number and Costs
        orderPhoneBaum=baum.getElementsByTagName("OrderPhone")
        if len(orderPhoneBaum)>0:
            self.orderphone.exists = True
            for fetched in orderPhoneBaum[0].childNodes:
                if fetched.nodeName == "Number":
                    self.orderphone.number = fetched.firstChild.data
                if fetched.nodeName == "CostPerCall":
                    self.orderphone.costspc = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.orderphone.currency = nycurrency
                    else:
                        self.orderphone.currency = self.currency
                if fetched.nodeName == "CostPerMinute":
                    self.orderphone.costspm = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.orderphone.currency = nycurrency
                    else:
                        self.orderphone.currency = self.currency
    
        #OrderFax: Number and Costs
        orderFaxBaum=baum.getElementsByTagName("OrderFax")
        if len(orderFaxBaum)>0:
            self.orderfax.exists = True
            for fetched in orderFaxBaum[0].childNodes:
                if fetched.nodeName == "Number":
                    self.orderfax.number = fetched.firstChild.data
                if fetched.nodeName == "CostPerCall":
                    self.orderfax.costspc = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.orderfax.currency = nycurrency
                    else:
                        self.orderfax.currency = self.currency

                if fetched.nodeName == "CostPerMinute":
                    self.orderfax.costspm = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.orderfax.currency = nycurrency
                    else:
                        self.orderfax.currency = self.currency
                    
        #Hotline: Number and Costs
        hotlineBaum=baum.getElementsByTagName("Hotline")
        if len(hotlineBaum)>0:
            self.hotline.exists = True
            for fetched in hotlineBaum[0].childNodes:
                if fetched.nodeName == "Number":
                    self.hotline.number = fetched.firstChild.data
                if fetched.nodeName == "CostPerCall":
                    self.hotline.costspc = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.hotline.currency = nycurrency
                    else:
                        self.hotline.currency = self.currency       

                if fetched.nodeName == "CostPerMinute":
                    self.hotline.costspm = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.hotline.currency = nycurrency
                    else:
                        self.hotline.currency = self.currency       
                

        #ForwardExpenses
        partBaum=baum.getElementsByTagName("ForwardExpenses")
        if len(partBaum)>0:
            for fetched in partBaum[0].childNodes:
                if fetched.nodeName == "FlatRate":
                    self.forwardexp.FlatrEx=True
                    self.forwardexp.FlatrVa=fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.forwardexp.FlatrCu = nycurrency
                    else:
                        self.forwardexp.FlatrCu = self.currency       

                if fetched.nodeName == "UpperBound":
                    self.forwardexp.BoundEx = True
                    self.forwardexp.BoundVa = fetched.firstChild.data
                    nycurrency = fetched.getAttribute("currency")
                    if len(nycurrency)>0:
                        self.forwardexp.BoundCu = nycurrency
                    else:
                        self.forwardexp.BoundCu = self.currency          
                                
        #Payment Methods
        partBaum=baum.getElementsByTagName("Payment")
        if len(partBaum)>0:
            o1BBTIA = False
            for eintrag in partBaum[0].childNodes:
                paymeth = self.PayStuff()                
                
                for fetched in eintrag.childNodes:                
                    if (fetched.nodeName == "Name") and (fetched.firstChild.data in listen.bezahlmethodenCODE):
                        paymeth.name=listen.bezahlmethodenCODE[fetched.firstChild.data]                   
                        paymeth.type=listen.bezahlmethodenTYPE[fetched.firstChild.data]
                    if (fetched.nodeName == "Surcharge"):
                        paymeth.kostenEX = True
                        paymeth.kosten = fetched.firstChild.data
                        nycurrency = fetched.getAttribute("currency")
                        if len(nycurrency)>0:
                             paymeth.kocurr = nycurrency
                        else:
                             paymeth.kocurr = self.currency

                    if (fetched.nodeName == "MaxSurcharge"):
                        paymeth.maxkosEX = True
                        paymeth.maxkosten = fetched.firstChild.data
          
                if not(paymeth.name==""):
                    if (paymeth.name!="BBTIA") or (o1BBTIA == False):
                        self.paymethods.append(paymeth)
                        if str(paymeth.name)=="BBTIA": o1BBTIA = True       

        #Special Offers
        partBaum=baum.getElementsByTagName("Features")
        if len(partBaum)>0:
            for eintrag in partBaum[0].childNodes:
                specoff = self.SpecialOfferStuff()       
                if (eintrag.nodeName in listen.possiblefeatures):
                    specoff.type = eintrag.nodeName
                    nyboolean = eintrag.getAttribute("surcharge")
                    if len(nyboolean)>0:
                        if (nyboolean[0].lower() == "y") or (nyboolean[0].lower() == "t") or (nyboolean[0].lower() == "1"):
                            specoff.unfree = True
                        else:
                            specoff.unfree = False
                    else:
                        specoff.unfree = True


                if not(specoff.type==""):
                    self.specoffers.append(specoff)                              


    def readProdCSV(self, datei="none"):
        if datei=="none":
            datei=self.updateM.url
                  
        csv.register_dialect("short_life", delimiter=self.updateM.delimiter,quotechar=self.updateM.quoted,escapechar=self.updateM.escaped)
        
        req = urllib.Request(url=datei, headers = { 'User-Agent' : 'elmar2goodrelations/1.0' })
        dat2 = urllib.urlopen(req, timeout=self.paramenter.timeout)
        reader = csv.reader(dat2, "short_life")
        
        self.tmpProdMetaData = listen.createHttpMetaDat(dat2.info(), self.paramenter, self.foldername, "products")
         
        for row in reader:
            try:
                linie = []
                for each in row:
                    linie.append(each.decode("latin-1"))
                self.produkte.append(linie) 
                self.produktecnt+=1
            except Exception, e:
                print "Error while appending row."
        csv.unregister_dialect("short_life")

                                   
    def writeShopRDF(self):  
        # Head
        if not os.path.isdir(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep):
            os.makedirs(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep)

        fobj = codecs.open(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep+"shop.rdf", "w+", "utf8")
        fobj.write("""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <!DOCTYPE rdf:RDF
      [<!ENTITY vcard \"http://www.w3.org/2006/vcard/ns#\">
       <!ENTITY xsd \"http://www.w3.org/2001/XMLSchema#\">
    ]>
    <rdf:RDF
      xmlns:dct=\"http://purl.org/dc/terms/\"
      xmlns:foaf=\"http://xmlns.com/foaf/0.1/\"
      xmlns:gr=\"http://purl.org/goodrelations/v1#\"
      xmlns:http=\"http://www.w3.org/2006/http#\"
      xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
      xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\"
      xmlns:status=\"http://www.w3.org/2008/http-statusCodes#\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema#\"
      xmlns:vcard=\"http://www.w3.org/2006/vcard/ns#\"
      xmlns:void=\"http://rdfs.org/ns/void#\" 
      xmlns=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/shop.rdf#\"
      xml:base=\"""" + self.paramenter.Sbaseuri + self.foldername + """/rdf/shop.rdf\">
    
<gr:BusinessEntity rdf:ID=\"BusinessEntity\">\n""")
        if self.name != "":
            fobj.write("  <rdfs:label xml:lang=\"" + self.language + "\">" + self.name + "</rdfs:label>\n")
        if self.urlseealso != "":
            fobj.write("  <foaf:page rdf:resource=\"" + self.urlseealso + "\"/>\n")
        if self.urllogo != "":
            fobj.write("  <foaf:depiction rdf:resource=\"" + self.urllogo + "\"/>\n")
        if self.description != "":
            fobj.write("  <rdfs:comment xml:lang=\"" + self.language + "\">" + self.description + "</rdfs:comment>\n")
        if self.orderphone.exists == True:
            fobj.write("""  <vcard:tel>\n    <vcard:Tel rdf:ID=\"order_tel\">
      <rdfs:label xml:lang=\"de\">Telefonnummer fuer Bestellungen</rdfs:label>
      <rdf:value>"""+ self.orderphone.number +"""</rdf:value>\n""")
            if self.orderphone.costspm != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.orderphone.costspm + " " + self.orderphone.currency + " pro Minute</rdfs:comment>\n")
            elif self.orderphone.costspc != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.orderphone.costspc + " " + self.orderphone.currency + " pro Anruf</rdfs:comment>\n")
            fobj.write("    </vcard:Tel>\n  </vcard:tel>\n") 
    
        if self.orderfax.exists == True:
            fobj.write("""  <vcard:fax>\n    <vcard:Fax rdf:ID=\"order_fax\">  
      <rdfs:label xml:lang=\"de\">Faxnummer fuer Bestellungen</rdfs:label>
      <rdf:value>"""+ self.orderfax.number +"""</rdf:value>\n""")
            if self.orderfax.costspm != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.orderfax.costspm + " " + self.orderfax.currency + " pro Minute</rdfs:comment>\n")
            elif self.orderfax.costspc != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.orderfax.costspc + " " + self.orderfax.currency + " pro Anruf</rdfs:comment>\n")
            fobj.write("    </vcard:Fax>\n  </vcard:fax>\n") 
    
        if self.hotline.exists == True:
            fobj.write("""  <vcard:tel>\n    <vcard:Tel rdf:ID=\"hotline_tel\">  
      <rdfs:label xml:lang=\"de\">Telefonhotline</rdfs:label>
      <rdf:value>"""+ self.hotline.number +"""</rdf:value>\n""")
            if self.hotline.costspm != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.hotline.costspm + " " + self.hotline.currency + " pro Minute</rdfs:comment>\n")
            elif self.hotline.costspc != "":
                fobj.write("      <rdfs:comment xml:lang=\"de\">" + self.hotline.costspc + " " + self.hotline.currency + " pro Anruf</rdfs:comment>\n")
            fobj.write("    </vcard:Tel>\n  </vcard:tel>\n")
        
        if self.adress1.exists == True:
            fobj.write("  <vcard:adr>\n    <vcard:Address rdf:ID=\"address_1\">\n")
            if self.publicemail != "":
                fobj.write("      <vcard:email>" + self.publicemail + "</vcard:email>\n")
    #        if self.adress1.compname != "":
    #            fobj.write("      <vcard:_________>" + self.adress1.compname + "</vcard:_________>\n")
            if self.adress1.street != "":
                fobj.write("      <vcard:street-address>" + self.adress1.street + "</vcard:street-address>\n")
            if self.adress1.postcode != "":
                fobj.write("      <vcard:postal-code>" + self.adress1.postcode + "</vcard:postal-code>\n")
            if self.adress1.city != "":
                fobj.write("      <vcard:locality>" + self.adress1.city + "</vcard:locality>\n")
            fobj.write("    </vcard:Address>\n  </vcard:adr>\n")
            
            if self.paramenter.ypfapikey != "":
                geo_tmp = ""
                geo_tmp = listen.createStringGeolocation(self.paramenter.ypfapikey, self.adress1, "1")
                if geo_tmp != "":
                    fobj.write(geo_tmp)
                    self.adress1.hasgeo=True
            
            if self.adress2.exists == True:
                fobj.write("  <vcard:adr>\n    <vcard:Address rdf:ID=\"address_2\">\n")
        #        if self.adress2.compname != "":
        #            fobj.write("      <vcard:_________>" + self.adress2.compname + "</vcard:_________>\n")
                if self.adress2.street != "":
                    fobj.write("      <vcard:street-address>" + self.adress2.street + "</vcard:street-address>\n")
                if self.adress2.postcode != "":
                    fobj.write("      <vcard:postal-code>" + self.adress2.postcode + "</vcard:postal-code>\n")
                if self.adress2.city != "":
                    fobj.write("      <vcard:locality>" + self.adress2.city + "</vcard:locality>\n")
                fobj.write("    </vcard:Address>\n  </vcard:adr>\n")
                
                if self.paramenter.ypfapikey != "":
                    geo_tmp = ""
                    geo_tmp = listen.createStringGeolocation(self.paramenter.ypfapikey, self.adress2, "2")
                    if geo_tmp != "":
                        fobj.write(geo_tmp)
                        self.adress2.hasgeo=True
        
        elif self.publicemail != "":
            fobj.write("  <vcard:adr>\n    <vcard:Address rdf:ID=\"address_1\">\n      <vcard:email>" + self.publicemail + "</vcard:email>\n    </vcard:Address>\n  </vcard:adr>\n")
            
        if self.adress1.sale == "yes":
            fobj.write("  <gr:hasPOS rdf:resource=\"#LOSOSP_1\"/>\n")
        if self.adress2.sale == "yes":
            fobj.write("  <gr:hasPOS rdf:resource=\"#LOSOSP_2\"/>\n")
        
        fobj.write("</gr:BusinessEntity>\n\n")
    
        if self.adress1.sale == "yes":
            if self.adress1.hasgeo == True:
                fobj.write("<gr:LocationOfSalesOrServiceProvisioning rdf:ID=\"LOSOSP_1\">\n  <rdfs:label xml:lang=\"" + self.language + "\">" + self.name + "</rdfs:label>\n  <vcard:adr rdf:resource=\"#address_1\"/>\n  <vcard:geo rdf:resource=\"#geoAddress_1\"/>\n</gr:LocationOfSalesOrServiceProvisioning>\n")
            else:
                fobj.write("<gr:LocationOfSalesOrServiceProvisioning rdf:ID=\"LOSOSP_1\">\n  <rdfs:label xml:lang=\"" + self.language + "\">" + self.name + "</rdfs:label>\n  <vcard:adr rdf:resource=\"#address_1\"/>\n</gr:LocationOfSalesOrServiceProvisioning>\n")
                
        if self.adress2.sale == "yes":
            if self.adress2.hasgeo == True:
                fobj.write("<gr:LocationOfSalesOrServiceProvisioning rdf:ID=\"LOSOSP_2\">\n  <rdfs:label xml:lang=\"" + self.language + "\">" + self.name + "</rdfs:label>\n  <vcard:adr rdf:resource=\"#address_2\"/>\n  <vcard:geo rdf:resource=\"#geoAddress_2\"/>\n</gr:LocationOfSalesOrServiceProvisioning>\n")
            else:
                fobj.write("<gr:LocationOfSalesOrServiceProvisioning rdf:ID=\"LOSOSP_2\">\n  <rdfs:label xml:lang=\"" + self.language + "\">" + self.name + "</rdfs:label>\n  <vcard:adr rdf:resource=\"#address_2\"/>\n</gr:LocationOfSalesOrServiceProvisioning>\n")

        if (self.tmpShopMetaData!=""):
            fobj.write("""<void:Dataset rdf:about=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/products.rdf#dataset\">
     <dct:source rdf:resource=\"""" + self.shopinfourl + """\"/> 
     <rdfs:seeAlso rdf:resource=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/products.rdf#ResponseMetaData\"/>
</void:Dataset>\n\n""" + self.tmpShopMetaData + """\n\n""")
        
        
        fobj.write("\n</rdf:RDF>")
        fobj.close()
        
    def writeProdCSV(self):
        if not os.path.isdir(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep):
            os.makedirs(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep)
            
        fobj = codecs.open(self.paramenter.outputdir+os.sep+self.foldername+os.sep+"rdf"+os.sep+"products.rdf", "w+", "utf8", errors="ignore")
        
        fobj.write("""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <!DOCTYPE rdf:RDF
      [<!ENTITY vcard \"http://www.w3.org/2006/vcard/ns#\">
      <!ENTITY xsd \"http://www.w3.org/2001/XMLSchema#\">
    ]>
    <rdf:RDF
      xmlns:dct=\"http://purl.org/dc/terms/\"
      xmlns:foaf=\"http://xmlns.com/foaf/0.1/\"
      xmlns:gr=\"http://purl.org/goodrelations/v1#\"
      xmlns:http=\"http://www.w3.org/2006/http#\"
      xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
      xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\"
      xmlns:status=\"http://www.w3.org/2008/http-statusCodes#\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema#\"
      xmlns:void=\"http://rdfs.org/ns/void#\"
      xmlns=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/products.rdf#\"
      xml:base=\"""" + self.paramenter.Sbaseuri + self.foldername + """/rdf/products.rdf\">\n\n""")
      
        #Hersteller schreiben
        if "brand" in self.updateM.spalten:
            spalte = self.updateM.spalten["brand"]-1
            brandlist = []
            
            for runner in self.produkte:
                try:
                    hersteller = runner[spalte]
                    if (brandlist.count(hersteller)==0) and (hersteller<>""): 
                        brandlist.append(hersteller)
                except IndexError:
                    del self.updateM.spalten["brand"]
                    break

           
            counter = 0
            for schluessel in brandlist:
                if counter==0:
                    counter+=1 
                    continue        
                        
                wert = "BE_"+str(counter)+"_"
                c = 0
                
                schluessel = listen.clearchars(schluessel, 0, True)
                schluessel = listen.replace_XMLEntities(schluessel)
                
                while c <> len(schluessel) and c<15:
                    if schluessel[c] in string.ascii_letters:
                        wert=wert+schluessel[c]
                    c+=1
                self.herstdict.update({schluessel: wert})
                
                fobj.write("""<gr:BusinessEntity rdf:ID=\""""+wert+"""\"> 
  <rdfs:label xml:lang=\""""+self.language+"""\">"""+schluessel+"""</rdfs:label>
  <rdfs:comment xml:lang=\""""+self.language+"""\">"""+schluessel+"""</rdfs:comment>
</gr:BusinessEntity>\n""")
                counter+=1
            
        #Offerings schreiben
        #
        i=0
        for runner in self.produkte:
            if i==0:
                i+=1 
                continue
            
            fobj.write("""\n<gr:Offering rdf:ID=\"Offering_"""+str(i)+"""\">
  <gr:includesObject>
    <gr:TypeAndQuantityNode rdf:ID=\"TypeAndQuantityNode_"""+str(i)+"""\">\n""")
            
            self.offeringnames.append("Offering_"+str(i))
            if ((self.adress1.sale=="yes") & (self.paramenter.usepos==True)):
                fobj.write("""      <gr:availableAtOrFrom rdf:resource=\"#LOSOSP_1\"/>\n""")
                
            if ((self.adress2.sale=="yes") & (self.paramenter.usepos==True)):
                fobj.write("""      <gr:availableAtOrFrom rdf:resource=\"#LOSOSP_2\"/>\n""")
                               
            fobj.write("""      <gr:amountOfThisGood rdf:datatype=\"&xsd;float\">1.0</gr:amountOfThisGood>
      <gr:hasUnitOfMeasurement rdf:datatype=\"&xsd;string\">C62</gr:hasUnitOfMeasurement>\n""")
            
        #ProductOrServicesSomeInstancesPlaceholder schreiben
        #Label und Comment erstellen
            complabel   = u""
            compcomment = u""

            try:
                if ("name" in self.updateM.spalten) and ("shortdescription" in self.updateM.spalten):
                    a = self.updateM.spalten["name"]-1
                    b = self.updateM.spalten["shortdescription"]-1
                    complabel = runner[a] + u" - " + runner[b]
                    
                elif ("name" in self.updateM.spalten) and ("shortdescription" not in self.updateM.spalten):
                    a = self.updateM.spalten["name"]-1
                    complabel = unicode(runner[a])
                    
                elif ("name" not in self.updateM.spalten) and ("shortdescription" in self.updateM.spalten):
                    b = self.updateM.spalten["shortdescription"]-1
                    complabel = unicode(runner[b])
                    
                elif ("name" not in self.updateM.spalten) and ("shortdescription" not in self.updateM.spalten):
                    complabel = u"Weder Name noch Kurzbeschreibung vorhanden."
            except Exception, e:
                print "compcomment unicode(runner) Error."
                complabel = u"Weder Name noch  Kurzbeschreibung kann gefunden werden."
                
            try:
                if ("type" in self.updateM.spalten) and ("longdescription" in self.updateM.spalten):
                    a = self.updateM.spalten["type"]-1
                    b = self.updateM.spalten["longdescription"]-1
                    compcomment = u"(Kategorie: " + runner[a] + u") - " + runner[b]
                    
                elif ("type" in self.updateM.spalten) and ("longdescription" not in self.updateM.spalten):
                    a = self.updateM.spalten["type"]-1
                    compcomment = unicode(runner[a])
                    
                elif ("type" not in self.updateM.spalten) and ("longdescription" in self.updateM.spalten):
                    b = self.updateM.spalten["longdescription"]-1
                    compcomment = unicode(runner[b])
                    
                elif ("type" not in self.updateM.spalten) and ("longdescription" not in self.updateM.spalten):
                    compcomment = u""
            except Exception, e:
                print "compcomment unicode(runner) Error."
                compcomment = u""
            
            complabel = listen.replace_XMLEntities(complabel)
            compcomment = listen.replace_XMLEntities(compcomment)
            
            fobj.write("""      <gr:typeOfGood>
        <gr:ProductOrServicesSomeInstancesPlaceholder rdf:ID=\"ProductOrServicesSomeInstancesPlaceholder_"""+str(i)+"""\">
          <rdfs:label xml:lang=\""""+self.language+"""\">"""+complabel+"""</rdfs:label>\n""")
            
            if not(compcomment == ""):
                fobj.write(u"""          <rdfs:comment xml:lang=\""""+self.language+"""\">"""+compcomment+"""</rdfs:comment>\n""")
            if (("privateid" in self.updateM.spalten) and (runner[self.updateM.spalten["privateid"]-1]<>"")):
                fobj.write("""          <gr:hasStockKeepingUnit rdf:datatype=\"&xsd;string\">"""+runner[self.updateM.spalten["privateid"]-1]+"""</gr:hasStockKeepingUnit>\n""")
            if (("ean" in self.updateM.spalten) and (runner[self.updateM.spalten["ean"]-1]<>"")):
                fobj.write("""          <gr:hasEAN_UCC-13 rdf:datatype=\"&xsd;string\">"""+runner[self.updateM.spalten["ean"]-1]+"""</gr:hasEAN_UCC-13>\n""")
            if ("brand" in self.updateM.spalten) and (runner[self.updateM.spalten["brand"]-1] in self.herstdict) and (self.herstdict[runner[self.updateM.spalten["brand"]-1]] <> "") and (self.herstdict[runner[self.updateM.spalten["brand"]-1]] <> None):
                fobj.write("""          <gr:hasManufacturer rdf:resource=\"#"""+self.herstdict[runner[self.updateM.spalten["brand"]-1]]+"""\"/>\n""")
            
            if (("deliverable" in self.updateM.spalten) and (runner[self.updateM.spalten["deliverable"]-1]<>"")):
                deliverable = runner[self.updateM.spalten["deliverable"]-1]
                fobj.write(listen.createStringDeliverable(deliverable, i))
                
            if (("url" in self.updateM.spalten) and (runner[self.updateM.spalten["url"]-1]<>"")):
                fobj.write("""          <foaf:page rdf:resource=\""""+listen.replace_XMLEntities(runner[self.updateM.spalten["url"]-1])+"""\"/>\n""")
                
            if (("pictureurl" in self.updateM.spalten) and (runner[self.updateM.spalten["pictureurl"]-1]<>"")):
                fobj.write("""          <foaf:depiction rdf:resource=\""""+listen.replace_XMLEntities(runner[self.updateM.spalten["pictureurl"]-1])+"""\"/>\n""")
                
            fobj.write("""        </gr:ProductOrServicesSomeInstancesPlaceholder>
      </gr:typeOfGood>
    </gr:TypeAndQuantityNode>
  </gr:includesObject>\n\n""")            
                            
            fobj.write("""  <gr:hasBusinessFunction rdf:resource=\"http://purl.org/goodrelations/v1#Sell\"/>
  <rdfs:label xml:lang=\""""+self.language+"""\">"""+complabel+"""</rdfs:label>\n""")
            
            if not(compcomment == ""):
                fobj.write(u"""  <rdfs:comment xml:lang=\""""+self.language+"""\">"""+compcomment+"""</rdfs:comment>\n""")
            if (("url" in self.updateM.spalten) and (runner[self.updateM.spalten["url"]-1]<>"")):
                fobj.write(u"""  <foaf:page rdf:resource=\""""+listen.replace_XMLEntities(runner[self.updateM.spalten["url"]-1])+"""\"/>\n""")
            if (("pictureurl" in self.updateM.spalten) and (runner[self.updateM.spalten["pictureurl"]-1]<>"")):
                fobj.write(u"""  <foaf:depiction rdf:resource=\""""+listen.replace_XMLEntities(runner[self.updateM.spalten["pictureurl"]-1])+"""\"/>\n""")
            if ("price" in self.updateM.spalten):
                fobj.write(u"""  <gr:hasPriceSpecification>
    <gr:UnitPriceSpecification rdf:ID=\"UPS_""" + str(i) + """\">
        <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">""" + runner[self.updateM.spalten["price"]-1].replace(',','.') + """</gr:hasCurrencyValue>
        <gr:hasUnitOfMeasurement rdf:datatype=\"&xsd;string\">C62</gr:hasUnitOfMeasurement>
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">""" + self.currency + """</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:UnitPriceSpecification>
  </gr:hasPriceSpecification>\n\n""")
                
            if ("deliverydetails" in self.updateM.spalten):
                fobj.write("""  <gr:hasPriceSpecification>
    <gr:DeliveryChargeSpecification rdf:ID=\"DCS_""" + str(i) + """\">\n""")
                if (self.forwardexp.BoundEx == True):
                    fobj.write("""      <rdfs:label xml:lang=\"""" + self.language + """\">Versandkostenfrei ab: """+self.forwardexp.BoundVa+" "+self.forwardexp.BoundCu+"""</rdfs:label>\n""")
                fobj.write("""      <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">""" + runner[self.updateM.spalten["deliverydetails"]-1].replace(',','.') + """</gr:hasCurrencyValue>
      <gr:hasCurrency rdf:datatype=\"&xsd;string\">""" + self.currency + """</gr:hasCurrency>
      <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:DeliveryChargeSpecification>
  </gr:hasPriceSpecification>\n\n""")
            elif (self.forwardexp.FlatrEx==True):
                fobj.write("""  <gr:hasPriceSpecification>
    <gr:DeliveryChargeSpecification rdf:ID=\"DCS_""" + str(i) + """\">\n""")
                if (self.forwardexp.BoundEx == True):
                    fobj.write("""      <rdfs:label xml:lang=\"""" + self.language + """\">Versandkostenfrei ab: """+self.forwardexp.BoundVa+" "+self.forwardexp.BoundCu+"""</rdfs:label>\n""")
                fobj.write("""      <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">""" + self.forwardexp.FlatrVa.replace(',','.') + """</gr:hasCurrencyValue>
      <gr:hasCurrency rdf:datatype=\"&xsd;string\">""" + self.forwardexp.FlatrCu + """</gr:hasCurrency>
      <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:DeliveryChargeSpecification>
  </gr:hasPriceSpecification>\n\n""")
                
            for each in self.paymethods:
                fobj.write("""  <gr:acceptedPaymentMethods rdf:resource=\"http://purl.org/goodrelations/v1#""" + each.type + """\"/>\n""")
                if (each.kostenEX == True) and (each.maxkosEX == True):
                    fobj.write("""    <gr:hasPriceSpecification>
    <gr:PaymentChargeSpecification rdf:ID=\"PCS_"""+ each.name + "_" + str(i) +"""\">
        <gr:appliesToPaymentMethod rdf:resource=\"http://purl.org/goodrelations/v1#"""+each.type+"""\"/>
        <gr:hasMinCurrencyValue rdf:datatype=\"&xsd;float\">""" + each.kosten.replace(',','.') + """</gr:hasMinCurrencyValue>
        <gr:hasMaxCurrencyValue rdf:datatype=\"&xsd;float\">""" + each.maxkosten.replace(',','.') + """</gr:hasMaxCurrencyValue>        
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">""" + each.kocurr + """</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded> 
    </gr:PaymentChargeSpecification>
  </gr:hasPriceSpecification>\n\n""")

                elif (each.kostenEX == True) and (each.maxkosEX == False):
                    fobj.write("""    <gr:hasPriceSpecification>
    <gr:PaymentChargeSpecification rdf:ID=\"PCS_"""+ each.name + "_" + str(i) +"""\">
        <gr:appliesToPaymentMethod rdf:resource=\"http://purl.org/goodrelations/v1#"""+each.type+"""\"/>
        <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">""" + each.kosten.replace(',','.') + """</gr:hasCurrencyValue>       
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">""" + each.kocurr + """</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded> 
    </gr:PaymentChargeSpecification>
  </gr:hasPriceSpecification>\n\n""")
            
            fobj.write("""</gr:Offering>\n\n""")
            
            i+=1
    
        for each in self.specoffers:
            theOutput, addOffering = listen.createStringSpecialOffers(each.type,each.unfree,self.urlseealso,self.currency)
            self.offeringnames.append(addOffering)
            fobj.write(theOutput)
        
        if len(self.offeringnames)>0:
            fobj.write("<gr:BusinessEntity rdf:about=\"" + self.paramenter.Snamespace + self.foldername + "/rdf/shop.rdf#BusinessEntity\">\n")
            for each in self.offeringnames:
                fobj.write("  <gr:offers rdf:resource=\"#" + each + "\"/>\n")
            fobj.write("</gr:BusinessEntity>\n")
        
        if (self.tmpProdMetaData!=""):
            fobj.write("""\n<void:Dataset rdf:about=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/products.rdf#dataset\">
     <dct:source rdf:resource=\"""" + self.updateM.url + """\"/> 
     <rdfs:seeAlso rdf:resource=\"""" + self.paramenter.Snamespace + self.foldername + """/rdf/products.rdf#ResponseMetaData\"/>
</void:Dataset>\n"""+ self.tmpProdMetaData + """\n""")
            
        fobj.write("</rdf:RDF>")
        fobj.close()
        return (i-1)