import lxml
import re
import time
import urllib
import urllib2
import logging
from pyquery import PyQuery as pq

class Parser:
    domain = ""

    def has_next(self):
        """Return if there are more RFPs left to parse"""
        raise NotImplementedError('Not implemented')

    def next(self, parse_each=True):
        """Return next (at most 10) parsed RFPs.
        
        Return list of dictionaries for each RFP. 
        If parse_each, then parse dedicated page of each RFP extracting
        additional metadata. Otherwise, return only parent ID, title, 
        and permanent URI of the RFP"""
        raise NotImplementedError('Not implemented')


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

    id_pattern = re.compile( 'id=(\d*)\&' )
    # Parsed listing of RFPs
    parsed_list = []

    pq = None
    request = None
    page = 1
    
        
    def has_next(self):
        """Return True if there is at least 1 more page of RFPs"""
        return self.page is not -1

    def next(self, parse_each=True):
        """Return next (at most 10) parsed RFPs.
        
        Return list of dictionaries for each RFP. 
        If parse_each, then parse dedicated page of each RFP extracting
        additional metadata. Otherwise, return only parent ID, title, 
        and permanent URI of the RFP"""

        rfp_list = []

        # load HTML for page with list of RFPs
        self.load( self.get_list_uri() )

        if self.request is None:
            raise IOError( 'Request object not initialized. Run load() first' )

        try:
            s = self.request.read()
            self.doc = pq( s )
        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse URI: %s' % self.list_uri )

        parse_list = self.parse_list()

        # Don't parse individual RFPs if not instructed to
        if not parse_each: 
            return parse_list

        # Load and parse each RFP's dedicated page to grab more detailed
        # information about each one
        for l in parse_list:
            try:
                self.load( (l['uri'],{}) )
                s = self.request.read()
                self.doc = pq( s )

                # Parse page's data and stash results in a dictionary
                rfp = self.parse_rfp()
                rfp['title'] = l['title']
                rfp['parent_id'] = l['parent_id']
                rfp['uri']  = l['uri']

                rfp_list.append( rfp )

            except lxml.etree.XMLSyntaxError as e:
                logging.error( 'Could not parse RFP: %s' % l.uri )

        return rfp_list

    # Private methods
    def parse_list(self):
        """Parse page with list of RFPs

        Assumes self.doc contains parsed DOM of list of RFPs page
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
            uri = MerxParser.domain + link.attr( "href" )
            id_search = self.id_pattern.search(uri)

            rfp = { 
                "title"     : link.text(),
                "uri"       : uri,
                "parent_id" : ( id_search is not None ) and id_search.group(1) or ""
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
        """Parse individual RFP page
        
        Assumes self.doc has parsed DOM tree of an RFP page"""
        rfp = {}

        labels = self.doc('.LabelRequired')
        table1 = labels.eq(0).siblings('table').find('tr td')
        table2 = labels.eq(2).siblings('table').find('tr td')
        table3 = labels.eq(4).siblings('table').find('tr td')
        table4 = labels.eq(6).siblings('table').find('tr td')

        rfp['org']             = table1.eq(8).text().strip()
        rfp['published_on']    = table2.eq(2).text().strip()
        rfp['parent_category'] = table3.eq(2).text().strip()
        rfp['description']     = table4.eq(1).text().strip()

        return rfp

    def load(self, request_data):
        """Load HTML from remote URI
        
        Do heavy lifting of feeding all the right magic data to Merx, 
        and stashing and reusing cookies"""
        uri  = request_data[0]
        data = request_data[1]

        try: 
            req = urllib2.Request(uri, data, self.headers)
            self.request = urllib2.urlopen(req)

            # stash away the cookies as we'll need them later for pagination (yeah..)
            if self.headers['Cookie'] is "":
                for h in self.request.info().headers:
                    if 'set-cookie' in h:
                        self.headers['Cookie'] = h[12:].replace(' path=/,', '')[:-7]
                        break

        except IOError as e:
            logging.error( 'Could not reach Merx at: %s' % self.list_uri )
            raise e

        return self

    def get_list_uri(self):
        """Return URI and POST data for the page with the list of RFPs"""
        if self.page is 1:
            uri  = self.domain + self.list_uri
            data = urllib.urlencode( self.list_data )
        else:
            # handle case of last page of results
            if self.page is -1:
                raise IOError( 'No more pages RFPs left to parse' )
            uri = self.domain + self.pagination_uri
            data = urllib.urlencode( self.pagination_data )

        return (uri, data)



def test():
    p = MerxParser()
    p.parse_next()
