import lxml
import re
import time
import urllib
import urllib2
import logging
from lib.pyquery import PyQuery as pq
import datetime
from HTMLParser import HTMLParser
import htmlentitydefs

class Parser:
    """All parsers should derive from this for a uniform API"""
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

    def parse_details(self, rpf):
        """Parse individual page of an RFP.

        rfp -- a dictionary containing metadata such as URI of the RFP page.
        """
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
        'txt_maxPerPage':'100'
    }
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2",
        "Cookie":""
    }

    # regex to extract ID of RFP from its URI
    id_pattern = re.compile( 'id=([^&]*)\&' )
    # Parsed listing of RFPs
    parsed_list = []

    # pyquery object
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
            rfp_list.append( self.parse_details(l) )

        return rfp_list


    def parse_details(self, l):
        try:
            self.load( (l['uri'], '') )
            s = self.request.read()
            self.doc = pq( s )

            # Parse page's data and stash results in a dictionary
            rfp = self.parse_rfp()
            rfp['title'] = l['title']
            rfp['original_id'] = l['original_id']
            rfp['origin'] = l['origin']
            rfp['uri']  = l['uri']


        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse RFP: %s' % l.uri )
            raise e

        return rfp

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
                "original_id" : ( id_search is not None ) and id_search.group(1) or "",
                'origin' : 'merx'
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
        
        Assumes self.doc contains parsed DOM tree of an RFP page"""
        rfp = {}

        labels = self.doc('.LabelRequired')
        table1 = labels.eq(0).siblings('table').find('tr td')
        table2 = labels.eq(2).siblings('table').find('tr td')
        table3 = labels.eq(4).siblings('table').find('tr td')
        table4 = labels.eq(6).siblings('table').find('tr td')
        table5 = labels.eq(8).siblings('table').find('tr td')

        rfp['org']             = table1.eq(8).text().strip()
        rfp['parsed_on'] = datetime.date.today()

        # date and time formats vary wildly on Merx. Use only date, and skip
        # problematic cases like empty dates
        try:
            rfp['published_on']    = datetime.datetime.strptime(
                    table2.eq(2).text().strip()[0:10], '%Y-%m-%d').date()
        # failed to parse publish date
        except ValueError as e:
            rfp['published_on'] = datetime.date.today()
            logging.error( "Couldn't parse publish date: %s" % rfp )

        try:
            rfp['ends_on'] = datetime.datetime.strptime(
                    table2.eq(8).text().strip()[0:10], '%Y-%m-%d').date()

        # failed to parse close date (more common that we'd like)
        except ValueError as e:
            rfp['ends_on'] = datetime.date.today() + datetime.timedelta(60)
            logging.error( "Couldn't parse close date: %s" % rfp )

        rfp['original_category'] = table3.eq(2).text().strip()
        rfp['location'] = table3.eq(11).text().strip()
        rfp['description'] = table4.eq(1).html().strip()

        if table5.eq(27).text() is not None:
            rfp['contact']     = table5.eq(27).text().strip()

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

class RFPParser(Parser):
    domain = 'http://www.rfp.ca/'
    login_url = 'login/'
    search_url = 'search_results_rfps/'

    headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2',
            'Cookie' : ''
              }
    
    login_parameters = {
            'action' : 'login',
            'username' : 'leslie_barron@hotmail.com',
            'password' : 'password',
            'return_url' : '',
            'keep' : 'false'
                       }

    doc = None

    def __init__(self):
        self.search_variables = '?action=search&listing_type%5Bequal%5D=RFP&keywords%5Bexact_phrase%5D=&Country%5Bmulti_like%5D%5B%5D=&State%5Bmulti_like%5D%5B%5D=&City%5Blike%5D=&PostedWithin%5Bmulti_like%5D%5B%5D='

    def has_next(self):
        return self.search_variables != None

    def parse_list(self):
        '''Parse page with list of RFPs

        Assumes self.doc contains parsed DOM of list of RFPs page
        '''

        parsed_list = []
        # parse the DOM looking for table rows of RFPs
        rows = self.doc('#listingsResults table tbody tr')

        logging.info('Got %s rows from RFP.ca' % len(rows))

        # extract RFP titles and links
        for i in range(0, len(rows), 4):
            link = rows.eq(i).find('td').eq(1).find('a').eq(1)
            id = rows.eq(i).find('td').eq(1).find('a').eq(0).attr('name').split('_')[1]

            rfp = { 
                'title'     : link.find('strong').text(),
                'uri'       : link.attr('href'),
                'original_id' : id,
                'origin' : 'rfpca'
            }

            parsed_list.append(rfp)


        next = self.doc('.pageNavigation a')

        has_next = False

        for i in range(len(next)):
            if next.eq(i).text() == 'Next':
                next = next.eq(i)
                has_next = True
                break

        if next != None:
            self.search_variables = next.attr('href')
        else:
            self.search_variables = None

        return parsed_list

    def next(self, parse_each=True):
        '''Return next (at most 10) parsed RFPs.
        
        Return list of dictionaries for each RFP. 
        If parse_each, then parse dedicated page of each RFP extracting
        additional metadata. Otherwise, return only parent ID, title, 
        and permanent URI of the RFP'''

        rfp_list = []

        # load HTML for page with list of RFPs
        self.setup(self.domain + self.search_url + self.search_variables)

        if self.doc is None:
            raise IOError( 'Doc object not initialized. Run setup() first' )

        parse_list = self.parse_list()

        # Don't parse individual RFPs if not instructed to
        if not parse_each: 
            return parse_list

        # Load and parse each RFP's dedicated page to grab more detailed
        # information about each one
        for l in parse_list:
            rfp_list.append(self.parse_details(l))

        return rfp_list

    def setup(self, uri):
        # login
        request = urllib2.Request(self.domain + self.login_url, urllib.urlencode(self.login_parameters), self.headers)
        response = urllib2.urlopen(request)
        
        # get cookie
        for i in range(len(response.info().headers)):
            if response.info().headers[i].startswith('Set-Cookie') or response.info().headers[i].startswith('set-cookie'):
                self.headers['Cookie'] = response.info().headers[i][12:].replace('; path=/', '')[:-2]



        # retrieve search list
        request = urllib2.Request(uri, headers = self.headers)
        response = urllib2.urlopen(request).read()

        try:
            self.doc = pq(response)
        except lxml.etree.XMLSyntaxError:
            logging.error('Could not parse URI: %s' % self.list_uri)

    def parse_details(self, l):
        
        try:
            # retrieve rfp doc list
            self.setup(l['uri'])

            rfp = {}

            # Parse page's data and stash results in a dictionary
            rfp = self.parse_rfp()
            rfp['title'] = l['title']
            rfp['original_id'] = l['original_id']
            rfp['origin'] = l['origin']
            rfp['uri'] = l['uri']


        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse RFP: %s' % l['uri'] )
            raise e

        return rfp

    def parse_rfp(self):
        """Parse individual RFP page
        
        Assumes self.doc contains parsed DOM tree of an RFP page"""
        rfp = {}

        info = self.doc('.listingInfo')
        list = info.find('.smallListingInfo')

        rfp['org'] = self.doc('.compProfileInfo strong:first').text()
        rfp['parsed_on'] = datetime.date.today()
        rfp['description'] = info.clone().children().remove().end().text()
        rfp['location'] = list.eq(2).text().split(': ')[1] + ', Canada'
        rfp['original_category'] = list.eq(3).text().split(': ')[1]


        # date and time formats vary wildly on Merx. Use only date, and skip
        # problematic cases like empty dates
        try:
            rfp['published_on']    = datetime.datetime.strptime(
                    list.eq(4).text().split(': ')[1], '%m.%d.%Y').date()
        # failed to parse publish date
        except ValueError as e:
            rfp['published_on'] = datetime.date.today()
            logging.error("Couldn't parse publish date: %s" % rfp)

        try:
            rfp['ends_on'] = datetime.datetime.strptime(
                    list.eq(5).text().split(': ')[1], '%m.%d.%Y').date()

        # failed to parse close date (more common that we'd like)
        except ValueError as e:
            rfp['ends_on'] = datetime.date.today() + datetime.timedelta(60)
            logging.error("Couldn't parse close date: %s" % rfp)

        return rfp        
    
class STParser(Parser):
    domain = 'http://www.sa-tenders.co.za/'

    headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2',
            'Cookie' : ''
              }
    
    def __init__(self):
        self.next_page = "tenderlist.asp?show=all"
        self.has_next_page = True

    def has_next(self):
        return self.has_next_page

    def parse_list(self):
        '''Parse page with list of RFPs

        Assumes self.doc contains parsed DOM of list of RFPs page
        '''

        parsed_list = []
        # parse the DOM looking for table rows of RFPs
        rows = self.doc('#line table tr table tr')
        
        next_page = rows.eq(0).find('td').eq(3)
        self.has_next_page = False
        self.next_page = ""
        if next_page.text() == "Next":
            self.next_page = next_page.find('a').eq(0).attr('href')
            self.has_next_page = True
        pagination = rows.pop(0)
        rows.pop(0)
        rows.pop()

        logging.info('Got %s rows from RFP.ca' % len(rows))

        # extract RFP titles and links
        for i in range(0, len(rows)):
            uri = rows.eq(i).find('td').eq(2).find('a').attr('href')
            ori_id = uri.split('=')[1]
            title = rows.eq(i).find('td').eq(0).text()
            rfp = { 
                'title'     : title,
                'uri'       : self.domain + uri,
                'original_id' : ori_id,
                'origin' : 'sa-tenders'
            }

            parsed_list.append(rfp)

        return parsed_list

    def next(self, parse_each=True):
        '''Return next (at most 10) parsed RFPs.
        
        Return list of dictionaries for each RFP. 
        If parse_each, then parse dedicated page of each RFP extracting
        additional metadata. Otherwise, return only parent ID, title, 
        and permanent URI of the RFP'''

        rfp_list = []

        # load HTML for page with list of RFPs
        self.setup(self.domain + self.next_page)

        if self.doc is None:
            raise IOError( 'Doc object not initialized. Run setup() first' )

        parse_list = self.parse_list()

        # Don't parse individual RFPs if not instructed to
        if not parse_each: 
            return parse_list

        # Load and parse each RFP's dedicated page to grab more detailed
        # information about each one
        for l in parse_list:
            rfp_list.append(self.parse_details(l))

        return rfp_list

    def setup(self, uri):
        
        # retrieve search list
        request = urllib2.Request(uri, headers = self.headers)
        response = urllib2.urlopen(request).read()

        try:
            self.doc = pq(response)
        except lxml.etree.XMLSyntaxError:
            logging.error('Could not parse URI: %s' % self.list_uri)

    def parse_details(self, l):
        
        try:
            # retrieve rfp doc list
            self.setup(l['uri'])

            rfp = {}

            # Parse page's data and stash results in a dictionary
            rfp = self.parse_rfp(l['uri'])
            rfp['title'] = l['title']
            rfp['original_id'] = l['original_id']
            rfp['origin'] = l['origin']


        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse RFP: %s' % l.uri )
            raise e

        return rfp

    def parse_rfp(self, uri):
        """Parse individual RFP page
        
        Assumes self.doc contains parsed DOM tree of an RFP page"""
        rfp = {}
        
        data = self.doc('#container').find('table').eq(3).find('tr')
        date_data = self.doc('#container').find('table').eq(3)
        
        try:
            rfp['published_on'] = datetime.datetime.strptime(
                    date_data.find('td').eq(7).text(), '%d %B %Y').date()
        # failed to parse publish date
        except ValueError as e:
            rfp['published_on'] = datetime.date.today()
            logging.error("Couldn't parse publish date: %s" % rfp)

        try:
            rfp['ends_on'] = datetime.datetime.strptime(
                    data.eq(4).find('td').eq(1).text(), '%d %B %Y').date()

        # failed to parse close date (more common that we'd like)
        except ValueError as e:
            rfp['ends_on'] = datetime.date.today() + datetime.timedelta(60)
            logging.error("Couldn't parse close date: %s" % rfp)

       
        rfp['org'] = data.eq(2).find('td').eq(1).text()
        rfp['parsed_on'] = datetime.date.today()
        rfp['description'] = strip_tags(data.eq(6).html()).replace("Description:", "").replace('\\n', '\n')
        rfp['location'] = 'none'
        rfp['original_category'] = data.eq(4).find('td').eq(1).text()
        rfp['uri'] = uri;

        # date and time formats vary wildly on Merx. Use only date, and skip
        # problematic cases like empty dates
        return rfp        
    
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
