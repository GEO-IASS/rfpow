import lxml
import urllib
import logging
from pyquery import PyQuery as pq

class Parser:
    domain = ""

class MerxParser(Parser):
    domain = "http://www.merx.com"

    @staticmethod
    def get_latest():
        """Return last 10 RFPs"""

        # You have to submit the search form to get a list of RFPs from Merx
        action_uri = MerxParser.domain + "/English/SUPPLIER_Menu.asp?WCE=GOTO"+\
                "&GID=REMOTESEARCH&TAB=1&PORTAL=MERX&"+\
                "hcode=xu%2b3MhJeX2npe2sJVPMRvQ%3d%3d"

        # pass the magic form data parameters
        data = urllib.urlencode( { 
            "PartnerId":"3", "SearchDB":"00", 
            "Keywords":"", "KeywordValue":"Search..."
        })

        # XXX: urlopen exception handling
        f = urllib.urlopen( action_uri, data )

        # parse the DOM of the results
        d = pq( f.read() )
        rows = d(".BoxBody_Center.FullSearchListBody_Center table tr")

        # remove title row and last row from results; they're useless CMS HTML
        rows.pop(0)
        rows.pop()
        logging.info( "Got %s rows from Merx" % len(rows) )

        result = []
        for i in range(0, len(rows)):
            link = rows.eq(i).find('td').eq(5).find('a')

            rfp = { 
                "title": link.text(),
                "link" : MerxParser.domain + link.attr( "href" )
            }

            result.append( rfp  )
            
        return result
