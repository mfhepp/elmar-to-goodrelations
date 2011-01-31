# Name:    elmar2gr /settings
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

Scurrency  = "EUR"                               # Standard Currency
Slanguage  = "DE"                                # Standard Language
Snamespace = "http://www.domain.tld/semantic/"   # Namespace
Sbaseuri   = "http://www.domain.tld/semantic/"   # Base URI
outputdir  = "output"                            # Local Directory where the files should be saved to.
listfile   = "shoplist.txt"                      # Textfile with the list shopinfo.xml who should be converted.
errorfile  = "errors.txt"                        # Filename for logging and errors.
startat    = 0                                   # For longer listfiles you can define which URI should be converted. 
endwith    = 0                                   # If you want to convert all of them, leave both at 0.
timeout    = 30               # Number of seconds to wait before raising an error
ypfapikey  = ""               # Enter here your yahoo! API key to convert addresses to geo locations. You can get one for free under: https://developer.apps.yahoo.com/
usepos     = False            # Activate only, if you are sure that ALL as available marked articles are available at all points of sale.
sitechangefreq = "weekly"     # How often will the individual data be updated?