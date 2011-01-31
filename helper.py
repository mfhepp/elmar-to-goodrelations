# Name:    elmar2gr /helper
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

import string
import json
import urllib2 as urllib
import urllib as urlencode
from datetime import datetime
import xml.dom.minidom as dom
import os

bezahlmethodenCODE={"debit":"DD",
                        "pre-payment":"BBTIA",
                        "money transfer":"BBTIA",
                        "cheque":"CIA",
                        "invoice":"BI",
                        "paypal":"PP",
                        "on delivery":"COD",
                        "amex":"AMEX",
                        "diners":"DINERS",
                        "eurocard":"EUROC",
                        "visa":"VISA"}

bezahlmethodenTYPE={"debit":"DirectDebit",
                        "pre-payment":"ByBankTransferInAdvance",
                        "money transfer":"ByBankTransferInAdvance",
                        "cheque":"CheckInAdvance",
                        "invoice":"ByInvoice",
                        "paypal":"PayPal",
                        "on delivery":"COD",
                        "amex":"AmericanExpress",
                        "diners":"DinersClub",
                        "eurocard":"MasterCard",
                        "visa":"VISA"}

DeliverableTrue  = ['1 - 3 Tage',
                    '1 bis 2 Tage',
                    '1 Tag',
                    '1 Werktag',
                    '1-2 Tage',
                    '1-2 Werktage',
                    '1-3 Tage',
                    '1-3 Werktage',
                    '2 - 3 Tage',
                    '2 Tage',
                    '2 Tage Lieferzeit',
                    '2 Werktage',
                    '2 Werktage nach Zahlungseingang',
                    '2-3 Tage',
                    '2-3 Werktage',
                    '24 h',
                    '24 Stunden',
                    '24h (per E-Mail)',
                    '3 Tage',
                    'ab Auslieferungslager',
                    'ab Auenlager',
                    'ab Lager',
                    "'ab Lager'",
                    'ab Lager Bchersendung innerhalb 1-4 Werktage',
                    'ab Lager lieferbar',
                    'ab Lager, sofort lieferbar',
                    'ab Lager/ 24Std.',
                    'ab Lager/Aussenlager',
                    'ab Lager/in Stock/en Stock',
                    'ab Zwischenlager',
                    'Alle Farben lieferbar',
                    'Am Lager',
                    'auf Lager',
                    'Auf Lager, sofort lieferbar',
                    'available',
                    'Bestellbestand',
                    'binnen 3 Werktage',
                    'ca 1-3 Tage',
                    'ca 2-3 Tage',
                    'ca. 1-2 Tage',
                    'ca. 1-3 Tage',
                    'ca. 2 Tage',
                    'ca. 2-3 Tage',
                    'ca. 3 Tage',
                    'ca. 3 Werktage',
                    'ca.1-3 Tage',
                    'ca.2-3 Tage',
                    'Der Artikel ist sofort versandfertig.',
                    'Expresslieferung',
                    'im Lager',
                    'in stock',
                    'innerhalb 24h versandfertig',
                    'Innerhalb von 24 Std. versandfertig.',
                    'Innerhalb von 24h versandfertig.',
                    'inStock',
                    'kurzfristig',
                    'kurzfristig lieferbar',
                    'Lager',
                    'lagernd',
                    'lagernd und sofort lieferbar',
                    'lagernd, Lieferzeit 1-2 Tage',
                    'Lagerware ca. 5 Werktage',
                    'lieferbar',
                    'lieferbar in 1 Tag(en)',
                    'lieferbar in 2 Tag(en)',
                    'lieferbar in 24h',
                    'lieferbar in 3 Tag(en)',
                    'Lieferzeit 1 - 4 Werktage',
                    'Lieferzeit 1- 4 Werktage',
                    'Lieferzeit 1-2 Tage',
                    'Lieferzeit 1-2 Tage solange der Vorrat reicht',
                    'Lieferzeit 1-2 Werktage',
                    'Lieferzeit 2 bis 3 Werktage',
                    'Lieferzeit 2-3 Tage',
                    'Lieferzeit 2-3 Werktage',
                    'Lieferzeit ca. 2-3Tage',
                    'Lieferzeit: 2-3 Werktage',
                    'Paketlaufzeit 2-3 Tage',
                    'sofort',
                    'Sofort [Artikel auf Lager]',
                    'sofort ab Lager',
                    'sofort bestellbar',
                    'Sofort Download',
                    'sofort lieferbar',
                    'Sofort lieferbar!',
                    'sofort lieferbar, innerhalb 24h versandfertig',
                    'Sofort nach Freigabe',
                    'sofort verfgbar',
                    'Sofort versandfertig.',
                    'sofort vorraetig',
                    'verfgbar',
                    'Verfgbar ab Lager',
                    'Versand innerhalb 24 Std',
                    'Versand innerhalb von 24 Stunden',
                    'Versandfertig ab Lager',
                    'versandfertig in 1 bis 2 Tagen',
                    'Versandfertig in 1-2 Werktagen',
                    'Versandfertig in 1-3 Werktagen',
                    'Versandfertig in 2 Tagen',
                    'Versandfertig in 3 Werktagen',
                    'voraussichtlich lieferbar:heute 24.05.2010',
                    'vorrtig in allen dNBb Shops',
                    'Wahr',
                    'Ware lagernd - versandfertig',
                    'Wenige Exemplare auf Lager - schnell bestellen!  Sofort versandfertig.',
                    'wenige lagernd',
                    'Y',
                    'yes']

DeliverableFalse = ['~ 3-4 Tage',
                    '-> auf Anfrage',
                    '-> Noch nicht lieferbar!',
                    '>7 Tage',
                    '1 - 2 Monate',
                    '1 - 2 Wochen',
                    '1 Woche',
                    '10 Tage',
                    '10-14 Tage',
                    '10-15 Tage',
                    '1-2 Wochen',
                    '14 Tage',
                    '1-4 Tage',
                    '14 Tage ab Bestellung',
                    '14 Werktage',
                    '14 Werktage nach Zahlungseingang',
                    '16 Tage',
                    '1-7 Tage',
                    '2 - 3 Monate',
                    '2 - 3 Wochen',
                    '2 - 4 Tage',
                    '2 bis 3 Tage',
                    '2 Wochen',
                    '2-10 Tage',
                    '2-3 Wochen',
                    '24 Tage',
                    '2-4 Tage',
                    '2-4 Werktage',
                    '2-4 Wochen',
                    '2-4Wochen.png',
                    '2-5 Tage',
                    '2-5 Tage (Nur bei Lagerware)',
                    '2-5 Werktage',
                    '2-5 Werktage ab Zahlungseingang',
                    '2-6 Tage',
                    '2-7 Werktage',
                    '3 - 5 Tage',
                    '3 bis 4 Werktage',
                    '3 bis 8 Tage, Mrz bis Nov.',
                    '3 Wochen',
                    '3-10 Werktage',
                    '3-4 Tage',
                    '3-4 Werktage',
                    '3-4 Werktage nach Geldeingang',
                    '3-4 Wochen',
                    '3-5 Tage',
                    '3-5 Werktage',
                    '3-6 Tage',
                    '3-6 Wochen',
                    '3-7 Tage nach Geldeingang',
                    '3-7 Werktage',
                    '3-9 Tage',
                    '4  5 Werktage',
                    '4 - 6 Wochen',
                    '4 Tage',
                    '4 Werktage',
                    '4-5 Tage',
                    '4-5 Werktage',
                    '4-6 Tage Lieferzeit',
                    '4-6 Werktage',
                    '4-9 Tage',
                    '5 - 7 Tage',
                    '5 Tage',
                    '5 Werktage',
                    '5-10 Tage',
                    '5-6 Tage',
                    '5-6 Werktage',
                    '5-7 Tage',
                    '5-7 Werktage',
                    '5-9 Werktage ab Zahlungseingang',
                    '7 - 14 Tage',
                    '7 Tage',
                    '7-14 Werktage',
                    '8-10 Tage',
                    '9 Tage',
                    'Artikel ausverkauft',
                    'Artikel derzeit nicht lieferbar',
                    'Artikel im Zulauf',
                    'Artikel in Bestellung',
                    'Artikel nicht lieferbar',
                    'Artikel nicht mehr lieferbar',
                    'Artikel noch in Vorbestellung',
                    'Artikel wird extra bestellt',
                    'Artikel wird fr Sie bestellt',
                    'auf Anfrage',
                    'auf Bestellung',
                    'auf Kundenanfrage',
                    'ausverkauft',
                    'bald lieferbar',
                    'Bestellbar',
                    'bestellt',
                    'Bestellware',
                    'binnen 1 Woche',
                    'bis ca. 10 Werktage',
                    'bis ca. 5 Werktage',
                    'ca 1 Woche',
                    'ca 10 Tage',
                    'ca 2-4 Tage',
                    'ca 3-4 Tage',
                    'ca 3-5 Tage',
                    'ca 5 Tage',
                    'ca 5-10 Tage',
                    'ca 5-7 Tage',
                    'ca 7 Tage',
                    'ca 7-10 Tage',
                    'ca. 1 Woche',
                    'ca. 10 Tage',
                    'ca. 10 Tage Lieferzeit',
                    'ca. 10 Werktage',
                    'ca. 1-2 Wochen',
                    'ca. 1-3 Wochen',
                    'ca. 14 Tage',
                    'ca. 15 Werktage',
                    'ca. 2 Woche',
                    'ca. 2 Wochen',
                    'ca. 20 Werktage',
                    'ca. 2-3 Wochen',
                    'ca. 2-4 Tage',
                    'ca. 28 Tage',
                    'ca. 3 -10 Werkt.',
                    'ca. 3-4 Tage',
                    'ca. 3-4 Wochen',
                    'ca. 3-5 Tage',
                    'ca. 3-7 Tage',
                    'ca. 4 Wochen',
                    'ca. 4-5 Tage',
                    'ca. 4-5 Wochen',
                    'ca. 4-6 Wochen',
                    'ca. 5 Tage',
                    'ca. 5 Werktage',
                    'ca. 5-7 Tage',
                    'ca. 5-7 Werktage',
                    'ca. 5-8 Tage',
                    'ca. 7 Tage',
                    'ca. 7 Werktage',
                    'ca. 7-10 Tage',
                    'ca. 8 Tage',
                    'ca.3-4 Tage',
                    'Dieser Artikel ist nicht mehr auf Lager und mu erst nachbestellt werden.Lieferzeiten von mehr als 4 Wochen sind zu erwarten.',
                    'Herstellungszeit ca. 4 Wochen ab Auftragseingang',
                    'im Zulauf',
                    'in 1-2 Wochen versandfertig',
                    'in ca. 1 - 3 Tagen versandfertig',
                    'in ca. 1 Woche versandfertig',
                    'innerhalb 1 Woche',
                    'innerhalb 4 Werktagen',
                    'Innerhalb von 10 Tagen versandfertig.',
                    'Innerhalb von 1-5 Tagen lieferbar.',
                    'Innerhalb von 21 Tagen versandfertig.',
                    'Innerhalb von 2-3 Tagen lieferbar.',
                    'Innerhalb von 3-5 Tagen lieferbar.',
                    'Innerhalb von 3-9 Tagen lieferbar',
                    'Lange, teils unklare Lieferzeit.',
                    'lieferbar in 120 Tag(en)',
                    'lieferbar in 14 Tag(en)',
                    'lieferbar in 20 Tag(en)',
                    'lieferbar in 21 Tag(en)',
                    'lieferbar in 2-3 Wochen',
                    'lieferbar in 30 Tag(en)',
                    'Lieferbar in 3-4Tagen',
                    'Lieferbar in 3-4Wochen',
                    'lieferbar in 3-5 Tagen',
                    'lieferbar in 4 Tag(en)',
                    'lieferbar in 5 Tag(en)',
                    'lieferbar in 6 Tag(en)',
                    'lieferbar in 60 Tag(en)',
                    'lieferbar in 7 Tag(en)',
                    'lieferbar in 90 Tag(en)',
                    'Lieferbar innerhalb von 5-7 Tagen',
                    'Liefertermin - bitte anfragen',
                    'Lieferzeit 14 Tage',
                    'Lieferzeit 1-4 Werktage',
                    'Lieferzeit 2-4 Werktage',
                    'Lieferzeit 3 - 7 Werktage',
                    'Lieferzeit 3 bis 4 Tage',
                    'Lieferzeit 3 bis 4 Werktage',
                    'Lieferzeit 3-4 Werktage',
                    'Lieferzeit 3-4 Werktage!',
                    'Lieferzeit 4 - 10 Werktage',
                    'Lieferzeit 4 bis 5 Werktage',
                    'Lieferzeit 4-10 Werktage',
                    'Lieferzeit 4-5 Werktage',
                    'Lieferzeit 7 Werktage!',
                    'Lieferzeit 7-10 Werktage',
                    'Lieferzeit bis 1 Woche',
                    'Lieferzeit ca. 1 Woche',
                    'Lieferzeit ca. 10 Tage',
                    'Lieferzeit ca. 10 Werktage',
                    'Lieferzeit ca. 10-14 Tage',
                    'Lieferzeit ca. 2 Wochen',
                    'Lieferzeit ca. 2-3 Wochen',
                    'Lieferzeit ca. 3 Wochen',
                    'Lieferzeit ca. 3-5 Tage',
                    'Lieferzeit ca. 3-5 Wochen',
                    'Lieferzeit ca. 3-5 Wochen.',
                    'Lieferzeit ca. 3-6 Tage',
                    'Lieferzeit ca. 4 Arbeitstage',
                    'Lieferzeit ca. 5 Werktage',
                    'Lieferzeit ca. 5-7 Werktage',
                    'Lieferzeit ca. 7-10 Tage',
                    'Lieferzeit ca. 7-14 Tage',
                    'Lieferzeit unbekannt',
                    'Lieferzeit: 3 bis 4 Werktage',
                    'Lieferzeit: 3-4 Werktage',
                    'Lieferzeit: 3-5 Werktage',
                    'Lieferzeit: 4-5 Werktage',
                    'Lieferzeit: 5 Werktage',
                    'Lieferzeit: 6-8 Werktage',
                    'Lieferzeitraum ohne Angaben',
                    'mehr als 2 Wochen',
                    'mittelfristig',
                    'momentan nicht lieferbar',
                    'Neuheit - noch nicht lieferbar',
                    'nicht ab Lager',
                    'nicht ab Lager lieferbar',
                    'nicht am Lager, Lieferzeit anfragen',
                    'nicht an Lager in krze wieder liefernar',
                    'nicht auf Lager',
                    'nicht lagernd',
                    'Nicht lieferbar',
                    'nicht lieferbar siehe Beschreibung',
                    'nicht mehr lieferbar',
                    'Nicht vorraetig',
                    'nicht vorrtig',
                    'not in stock',
                    'nur Vorbestellung',
                    'Pre-Order, Release unbekannt',
                    'sobald verfgbar',
                    'vergriffen',
                    'verkauft',
                    'Versand innerhalb von 3-4 Tagen',
                    'Versandfertig in 1-2 Wochen',
                    'Versandfertig in 2 Wochen',
                    'versandfertig in 2-5 Werktagen',
                    'Versandfertig in 3 - 7 Werktagen',
                    'Versandfertig in 3 Wochen',
                    'Versandfertig in 3-5 Arbeitstage',
                    'Versandfertig in 3-5 Werktagen',
                    'Versandfertig in 4 Wochen',
                    'Versandfertig in 5 Werktagen',
                    'Versandfertig in ca. 2 bis 4 Tagen ab Bestellung',
                    'voraussichtlich 1-2 Wochen',
                    'voraussichtlich lieferbar:nicht bekannt',
                    'Ware bestellt',
                    'wird bestellt',
                    'wird fr Sie bestellt',
                    'wird fr Sie hergestellt',
                    'z.Zt. nicht lieferbar',
                    'zur Zeit leider nicht lieferbar',
                    'zur Zeit nicht lieferbar',
                    'zur Zeit vergriffen']

possiblefeatures = ["InstallationAssistance",
                    "RepairService",
                    "CareAfterPurchase",
                    "GiftService"]

def createStringDeliverable(deliverable, number):
    deliverable = clearchars(deliverable,0,True)
    if (deliverable in DeliverableTrue):
        return("""          <gr:hasInventoryLevel>
            <gr:QuantitativeValueFloat rdf:ID=\"InventoryLevel_"""+str(number)+"""\">
              <gr:hasMinValueFloat rdf:datatype=\"&xsd;float\">1.0</gr:hasMinValueFloat>
              <gr:hasUnitOfMeasurement rdf:datatype=\"&xsd;string\">C62</gr:hasUnitOfMeasurement>
              <rdfs:label xml:lang=\"de\">Verfuegbarkeit: """+deliverable+"""</rdfs:label>
            </gr:QuantitativeValueFloat>
          </gr:hasInventoryLevel>\n""")
    
    if (deliverable in DeliverableFalse):
        return("""          <gr:hasInventoryLevel>
            <gr:QuantitativeValueFloat rdf:ID=\"InventoryLevel_"""+str(number)+"""\">
              <gr:hasValueFloat rdf:datatype=\"&xsd;float\">0.0</gr:hasValueFloat>
              <gr:hasUnitOfMeasurement rdf:datatype=\"&xsd;string\">C62</gr:hasUnitOfMeasurement>
              <rdfs:label xml:lang=\"de\">Verfuegbarkeit: """+deliverable+"""</rdfs:label>
            </gr:QuantitativeValueFloat>
          </gr:hasInventoryLevel>\n""")
    
    else:
        return("""""")

   
def createStringSpecialOffers(feature, unfree, theLink, currency):
    if (feature=="InstallationAssistance"):
        theLabel ="<rdfs:label xml:lang=\"de\">Installationsservice</rdfs:label>"
        theBusFu ="<gr:hasBusinessFunction rdf:resource=\"http://purl.org/goodrelations/v1#ConstructionInstallation\"/>"
        if (unfree==True):
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenpflichtiger Installationsservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S01\">"
            theOfferingName = "Offering_S01"
            thePrice = ""
        else:
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenloser Installationsservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S02\">"
            theOfferingName = "Offering_S02"
            thePrice = """    <gr:hasPriceSpecification>
    <gr:UnitPriceSpecification rdf:ID=\"UPS_S01\">
        <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">0.00</gr:hasCurrencyValue>
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">"""+currency+"""</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:UnitPriceSpecification>
  </gr:hasPriceSpecification>\n"""
            
    if (feature=="RepairService"):
        theLabel ="<rdfs:label xml:lang=\"de\">Reparaturservice</rdfs:label>"
        theBusFu ="<gr:hasBusinessFunction rdf:resource=\"http://purl.org/goodrelations/v1#Repair\"/>"
        if (unfree==True):
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenpflichtiger Reparaturservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S03\">"
            theOfferingName = "Offering_S03"
            thePrice = ""
        else:
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenloser Reparaturservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S04\">"
            theOfferingName = "Offering_S04"
            thePrice = """    <gr:hasPriceSpecification>
    <gr:UnitPriceSpecification rdf:ID=\"UPS_S02\">
        <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">0.00</gr:hasCurrencyValue>
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">"""+currency+"""</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:UnitPriceSpecification>
  </gr:hasPriceSpecification>\n"""
                    
    if (feature=="CareAfterPurchase"):
        theLabel ="<rdfs:label xml:lang=\"de\">Dienstleistungen nach dem Kauf</rdfs:label>"
        theBusFu ="<gr:hasBusinessFunction rdf:resource=\"http://purl.org/goodrelations/v1#Maintain\"/>"
        if (unfree==True):
            theComment = "<rdfs:comment xml:lang=\"de\">Es werden kostenpflichtige Dienstleistungen nach dem Kauf angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S05\">"
            theOfferingName = "Offering_S05"
            thePrice = ""
        else:
            theComment = "<rdfs:comment xml:lang=\"de\">Es werden kostenlose Dienstleistungen nach dem Kauf angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S06\">"
            theOfferingName = "Offering_S06"
            thePrice = """    <gr:hasPriceSpecification>
    <gr:UnitPriceSpecification rdf:ID=\"UPS_S05\">
        <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">0.00</gr:hasCurrencyValue>
        <gr:hasCurrency rdf:datatype=\"&xsd;string\">"""+currency+"""</gr:hasCurrency>
        <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
    </gr:UnitPriceSpecification>
  </gr:hasPriceSpecification>\n"""
            
    if (feature=="GiftService"):
        theLabel ="<rdfs:label xml:lang=\"de\">Geschenkeservice</rdfs:label>"
        theBusFu ="<gr:hasBusinessFunction rdf:resource=\"http://purl.org/goodrelations/v1#ProvideService\"/>"
        if (unfree==True):
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenpflichtiger Geschenkeservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S07\">"
            theOfferingName = "Offering_S07"
            thePrice = ""
        else:
            theComment = "<rdfs:comment xml:lang=\"de\">Es wird ein kostenloser Geschenkeservice angeboten.</rdfs:comment>"
            theID = "<gr:Offering rdf:ID=\"Offering_S08\">"
            theOfferingName = "Offering_S08"
            thePrice = """    <gr:hasPriceSpecification>
      <gr:UnitPriceSpecification rdf:ID=\"UPS_S07\">
          <gr:hasCurrencyValue rdf:datatype=\"&xsd;float\">0.00</gr:hasCurrencyValue>
          <gr:hasCurrency rdf:datatype=\"&xsd;string\">"""+currency+"""</gr:hasCurrency>
          <gr:valueAddedTaxIncluded rdf:datatype=\"&xsd;boolean\">true</gr:valueAddedTaxIncluded>
      </gr:UnitPriceSpecification>
    </gr:hasPriceSpecification>\n"""
    
    theReturn = theID + """\n    """+theBusFu+"""\n    """+theLabel+"""\n    """+theComment+"""\n    <foaf:page rdf:resource=\""""+theLink+"""\"/>\n"""+thePrice+"""</gr:Offering>\n"""
    
    return(theReturn, theOfferingName)

def createStringGeolocation(apikey, address, appendix):
    loc     = urlencode.quote(clearchars(address.street,0)+", "+clearchars(address.postcode,0)+", "+clearchars(address.city,0))
    url     = "http://where.yahooapis.com/geocode?location=" + loc + "&apikey=" + apikey
    datei   = urllib.urlopen(url, timeout=10)
    content = datei.read()
    baum = dom.parseString(content)
    text = ""
    if (baum.getElementsByTagName("Found")[0].firstChild.data=="1"):
        text = "  <vcard:geo>\n    <rdf:Description rdf:ID=\"geoAddress_"+appendix+"\">\n      <vcard:latitude rdf:datatype=\"&xsd;float\">"+baum.getElementsByTagName("latitude")[0].firstChild.data+"</vcard:latitude>\n      <vcard:longitude rdf:datatype=\"&xsd;float\">"+baum.getElementsByTagName("longitude")[0].firstChild.data+"</vcard:longitude>\n    </rdf:Description>\n  </vcard:geo>\n"
        print "Geolocation created!"
    return text


def replace_XMLEntities(text):
    XML_dic = {'<':'&lt;', '>':'&gt;', '&':'&amp;'}
    for i, j in XML_dic.iteritems():
        text = text.replace(i, j)
    return text


def clearchars(input, max, moreYN=False):
    new = ""
    if (moreYN==True):
        allowed = string.printable
    else:
        allowed = string.letters+string.digits
        
    c=0
    
    for each in input:
        c=+1
        if each in allowed:
            new=new+each
        if ((c==max) and (max!=0)):
            break
    return new

def clearedurl(url):
    if url.startswith("http://"):
        url=url[7:]
    if url.startswith("https://"):
        url=url[8:]
    if url.startswith("www."):
        url=url[4:]
    if url.endswith("shopinfo.xml"):
        url=url[:-12]
    if url.endswith("/"):
        url=url[:-1]
    if url.endswith("/index.html"):
        url=url[:-11]
    if url.endswith("/index.htm"):
        url=url[:-10]
    if url.endswith("/catalog"):
        url=url[:-8]
        
    url=url.replace(".","_")
    url=url.replace("/","_")
    url=url.replace(",","_")
    return url;
    
def clearedname(name):
    new = ""
    if name.startswith("http://"):
        name=name[7:]
    if name.startswith("www."):
        name=name[4:]
    if name.endswith("shopinfo.xml"):
        name=name[:-12] 
    c=0    
    for each in name:
        c=+1
        if each in string.letters or each in string.digits:
            new=new+each
        if c==25:
            break
    return new

def createSingleSitemap (shopname, baseuri, fileprefixes, changefreq):
    data = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"
        xmlns:sc=\"http://sw.deri.org/2007/07/sitemapextension/scschema.xsd\">
   <sc:dataset>
     <sc:datasetLabel>"""+shopname+"""s Shopinfos and Products</sc:datasetLabel>
     <sc:linkedDataPrefix slicing=\"subject-object\">"""+ baseuri + fileprefixes+"""/rdf/shop.rdf#</sc:linkedDataPrefix>
     <sc:linkedDataPrefix slicing=\"subject-object\">"""+ baseuri + fileprefixes+"""/rdf/products.rdf#</sc:linkedDataPrefix>
     <sc:sampleURI>"""+baseuri + fileprefixes+"""/rdf/shop.rdf#BusinessEntity</sc:sampleURI>
     <sc:sampleURI>"""+baseuri + fileprefixes+"""/rdf/products.rdf#Offering_1</sc:sampleURI>
     <sc:dataDumpLocation>"""+baseuri + fileprefixes+"""/data/shop.rdf.gz</sc:dataDumpLocation>
     <sc:dataDumpLocation>"""+baseuri + fileprefixes+"""/data/products.rdf.gz</sc:dataDumpLocation>
     <changefreq>"""+changefreq+"""</changefreq>
     <lastmod>"""+str(datetime.now().replace(microsecond=0).isoformat())+"""</lastmod>
   </sc:dataset>
</urlset>"""
    return data

def createPartMainSitemap (base, folder):      
    data = """    <sitemap>
        <loc>"""+base+folder+"""/sitemap.xml</loc>
        <lastmod>"""+str(datetime.now().replace(microsecond=0).isoformat())+"""</lastmod>
    </sitemap>\n"""
    return data

def createHttpMetaDat(responseInfo, namespace, baseuri, outputdir, foldername):
    tmp = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
    <!DOCTYPE rdf:RDF
      [<!ENTITY vcard \"http://www.w3.org/2006/vcard/ns#\">
       <!ENTITY xsd \"http://www.w3.org/2001/XMLSchema#\">
    ]>
    <rdf:RDF
      xmlns:dct=\"http://purl.org/dc/terms/\"
      xmlns:headers=\"http://www.w3.org/2008/http-headers#\"
      xmlns:http=\"http://www.w3.org/2006/http#\"
      xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
      xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\"
      xmlns:status=\"http://www.w3.org/2008/http-statusCodes#\"
      xmlns:void=\"http://rdfs.org/ns/void#\"
      xmlns:xsd=\"http://www.w3.org/2001/XMLSchema#\">
      xmlns=\"""" + namespace + foldername + """/rdf/meta-information.rdf#\"
      xml:base=\"""" + baseuri + foldername + """/rdf/meta-information.rdf\">

    <Response rdf:about=\"ResponseMetaData\">\n"""
    
    if (responseInfo.getheader('Date')):
        tmp = tmp + """        <dct:date rdf:datatype=\"&xsd;datetime\">"""+ responseInfo.getheader('Date') +"""</dct:date>\n"""
    
    if (responseInfo.getheader('Server')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Server</fieldName>
            <fieldValue>"""+ responseInfo.getheader('Server') +"""</fieldValue>
        </headers>\n"""
    
    if (responseInfo.getheader('Last-Modified')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Last-Modified</fieldName>
            <fieldValue rdf:datatype=\"&xsd;datetime\">"""+ responseInfo.getheader('Last-Modified') +"""</fieldValue>
        </headers>\n"""
        
    if (responseInfo.getheader('Content-Length')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Content-Length</fieldName>
            <fieldValue rdf:datatype=\"&xsd;integer\">"""+ responseInfo.getheader('Content-Length') +"""</fieldValue>
        </headers>\n"""
    
    if (responseInfo.getheader('Content-Type')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Content-Type</fieldName>
            <fieldValue rdf:datatype=\"&xsd;string\">"""+ responseInfo.getheader('Content-Type') +"""</fieldValue>
        </headers>\n"""
    
    if (responseInfo.getheader('ETag')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>ETag</fieldName>
            <fieldValue rdf:datatype=\"&xsd;string\">"""+ responseInfo.getheader('ETag') +"""</fieldValue>
        </headers>\n"""
    
    if (responseInfo.getheader('Accept-Ranges')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Accept-Ranges</fieldName>
            <fieldValue rdf:datatype=\"&xsd;string\">"""+ responseInfo.getheader('Accept-Ranges') +"""</fieldValue>
        </headers>\n"""
    
    if (responseInfo.getheader('Connection')):
        tmp = tmp + """        <headers rdf:parseType=\"Resource\">
            <rdf:type rdf:resource=\"&http;MessageHeader\"/>
            <fieldName>Connection</fieldName>
            <fieldValue rdf:datatype=\"&xsd;string\">"""+ responseInfo.getheader('Connection') +"""</fieldValue>
        </headers>\n"""
    
    tmp = tmp + """        <httpVersion>1.1</httpVersion>
        <sc rdf:resource=\"http://www.w3.org/2008/http-statusCodes#statusCode200\"/>
        <statusCodeNumber>200</statusCodeNumber>
    </Response>"""
    
    print tmp
    return True