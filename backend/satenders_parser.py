import lxml
import re
import urllib
import urllib2
import datetime
from lib.pyquery import PyQuery
import logging
from backend.parsers import Parser
from HTMLParser import HTMLParser
import htmlentitydefs

class RFPParser(Parser):
    domain = 'http://www.sa-tenders.co.za/'

    headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2',
            'Cookie' : ''
              }
    
    doc = None

    def __init__(self):
        self.next_page = "tenderlist.asp?show=all"
        self.has_next = True

    def has_next(self):
        return has_next

    def parse_list(self):
        '''Parse page with list of RFPs

        Assumes self.doc contains parsed DOM of list of RFPs page
        '''

        parsed_list = []
        # parse the DOM looking for table rows of RFPs
        rows = self.doc('#line table tr table tr')
        
        next_page = rows.eq(0).find('td').eq(3)
        self.has_next = False
        self.next_page = None
        if next_page.text() == "Next":
            self.next_page = next_page.attr('href')
            self.has_next = True
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
            self.doc = PyQuery(response)
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
        rfp['description'] = repr(strip_tags(data.eq(6).html()))
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
