# ELMAR to GoodRelations #

## Aim and Benefits ##

This python script converts a given URI that points to a valid ELMAR shopinfo.xml file into a proper GoodRelations representation.

Using this script you can make the unique features of your products and services accessible for Semantic Web applications, novel mobile applications, and browser plug-ins.


## Features ##

  1. GoodRelations shop and product descriptions as RDF/XML
  1. Batch-processing to convert a large set of shops
  1. Automatic sitemap file generation

## Installation ##

> ### Step 1: Install Python ###
> This script is programmed and tested with Python 2.6. You need to have it installed to run the script.
> See http://docs.python.org/release/2.6.4/ for further details.

> ### Step 2: Download and Unpack elmar2gr ###
> Download the "elmar-to-goodrelations" zip-file and unpack it in a folder.
> This folder should now contain the following files:
    * elmar2gr.py  -> The main part of the script. Start this!
    * helper.py  -> Some external functions and variables.
    * mainloops.py  -> This part will do most of the work.
    * shoplist.txt  -> A set of example-URIs for a quick test.
    * settings.py  -> The settings-file.

> ### Step 3: Change Settings ###
> Now you need to edit the settings so that the script suits your needs.

> The customizations are done within the "settings.py"-file.
    * **Scurrency/Slanguage:** Enter which language and currency should be used if no other information is given.
    * **Snamespace/Sbaseuri:** Enter the URI where you plan to publish the converted data.
    * **listfile:** This points at a textfile which contains a list of the URI which should be converted.
    * **startat/endwith:** If you want to convert all URI in the listfile set these values to 0. If not, you can define the start- and endpoint of the conversion.
    * **ypfapikey:** Enter here your yahoo! API key to convert addresses to geo locations. You can get one for free under: https://developer.apps.yahoo.com/
    * **usepos:** Activate only, if you are sure that ALL as available marked articles are available at all points of sale.

> If you change anything, make sure that you use the scheme of the examples. E.g. if you change the output folder to "myoutput/" instead of "myoutput", the script won't work properly.

## Conversion ##

Start "elmar2gr.py", any error will be displayed and saved within the error-file (normally "errors.txt").
When the script is done, all you have to do is to upload the content of the output-directory to the location specified as "settings.Snamespace".

## GoodRelations ##

GoodRelations is a language that can be used to describe very precisely what your business is offering. You can use GoodRelations to create a small data package that describes your products and their features and prices, your stores and opening hours, payment options and the like.

See http://purl.org/goodrelations/ for further details.