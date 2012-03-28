import lxml
import re
import urllib
import urllib2
import datetime
from lib.pyquery import PyQuery
from backend.parsers import Parser
import logging

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
        if(response.info().headers[6].startswith('Set-Cookie')):
            self.headers['Cookie'] = response.info().headers[6][12:].replace('; path=/', '')[:-2]

        # retrieve search list
        request = urllib2.Request(uri, headers = self.headers)
        response = urllib2.urlopen(request).read()

        try:
            self.doc = PyQuery(response)
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


        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse RFP: %s' % l.uri )
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
        rfp['original_category'] = list.eq(3).text().split(': ')[1]
        rfp['uri'] = self.doc('.listingInfo a').text()
        print rfp['uri']

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
