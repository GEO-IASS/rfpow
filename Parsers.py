import lxml
import time
import urllib
import urllib2
import logging
from pyquery import PyQuery as pq

class Parser:
    domain = ""


class MerxParser(Parser):
    """A parser for merx.com"""

    domain = "http://www.merx.com"
    list_uri = "/English/SUPPLIER_Menu.asp?WCE=GOTO"+\
            "&GID=REMOTESEARCH&TAB=1&PORTAL=MERX&"+\
            "hcode=xu%2b3MhJeX2npe2sJVPMRvQ%3d%3d"
    list_data = { 
        "PartnerId":"3", "SearchDB":"00", 
        "Keywords":"", "KeywordValue":"Search..."
    }

    pagination_uri = ''
    pagination_data =  {
        'KeywordValue':'Search...',
        'SEARCH_BY_CONTEXT':'OO',
        'SEARCH_SINCE':'  ALL',
        'ospQuickSearch':'Search...',
        'search_profile':'',
        'txt_maxPerPage':'10'
    }
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2",
        "Cookie":""
    }

    # Parsed listing of RFPs
    parsed_list = []

    pq = None
    request = None
    page = 1
    
    def load(self):
        """Load HTML from remote URI"""
        # we're parsing the first page of results
        if self.page is 1:
            uri  = self.domain + self.list_uri
            data = urllib.urlencode( self.list_data )
        else:
            # handle case of last page of results
            if self.page is -1:
                raise IOError( 'No more pages RFPs left to parse' )
            uri = self.domain + self.pagination_uri
            data = urllib.urlencode( self.pagination_data )

        # pass the magic form data parameters
        try: 
            #import pdb; pdb.set_trace()
            logging.debug( 'Loading RFPs from: %s\n POST data: %s' % (uri, data ) )
            req = urllib2.Request(uri, data, self.headers)
            response = urllib2.urlopen(req)
            self.request = urllib2.urlopen( req )

            # stash away the cookies as we'll need them for pagination (yeah..)
            if self.headers['Cookie'] is "":
                for h in self.request.info().headers:
                    if 'set-cookie' in h:
                        self.headers['Cookie'] = h[12:].replace(' path=/,', '')[:-7]
                        break

        except IOError as e:
            logging.error( 'Could not reach Merx at: %s' % self.list_uri )
            raise e

        return self

        
    def has_next(self):
        """Return True if there is at least 1 more page of RFPs"""
        return self.page is not -1

    def parse_next(self):
        """Load and parse the next 10 RFPs, if available"""

        master_list = []
        for i in range(10):
            # load HTML first

            self.load()

            if self.request is None:
                raise IOError( 'Request object not initialized. Try load() first' )

            try:
                s = self.request.read()
                self.doc = pq( s )
            except lxml.etree.XMLSyntaxError as e:
                logging.error( 'Could not parse URI: %s' % self.list_uri )

            master_list = master_list + self.parse_list()
            time.sleep(2)

        return master_list


    def parse_list(self):
        """Parse list of RFPs from Merx

        Assumes that self.pq contains parsed list of RFPs
        """

        self.parsed_list = []
        # parse the DOM looking for table rows of RFPs
        rows = self.doc(".BoxBody_Center.FullSearchListBody_Center table tr")

        # remove title row and last row from self.parsed_lists; they're garbage HTML
        rows.pop(0)
        pagination = rows.pop()

        logging.info( "Got %s rows from Merx" % len(rows) )

        # extract RFP titles and links
        for i in range(0, len(rows)):
            link = rows.eq(i).find('td').eq(5).find('a')

            rfp = { 
                "title": link.text(),
                "link" : MerxParser.domain + link.attr( "href" )
            }

            self.parsed_list.append( rfp )

        pagination_links = pq( pagination ).find( '.NavLinkStyleLink' )
        next_page = pagination_links.eq( len(pagination_links)-1 )


        # This is the last page. Mark it for future reference
        # XXX: test stopping at last page
        if next_page.text().strip() != "Next":
            self.page = -1
            logging.debug( 'Reached last self.parsed_lists page' )
        else:
            self.page = self.page + 1
            self.pagination_uri = next_page.parent().attr('onclick')[14:-3]
            # more Merx's stupid magic values
            self.pagination_data[ 'search_profile' ] = self.doc( 'input' ).eq(0).val()

        return self.parsed_list
            

    def parse_rfp(self):
        """Parse individual RFP page"""
        return None


def test():
    p = MerxParser()
    p.parse_next()
