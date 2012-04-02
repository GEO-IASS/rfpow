import unittest
import logging
import inspect
import re
import datetime
import lxml
from lib.pyquery import PyQuery as pq
from backend.parsers import RFPParser, MerxParser



class RFPParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = RFPParser()

    def testSetup(self):
        self.parser.setup(self.parser.domain + self.parser.search_url + self.parser.search_variables)
        
        # Make sure the PHPSESSID cookie is present
        self.assertTrue(self.parser.headers['Cookie'].find('PHPSESSID=') != -1)

        # The doc should contain the list of 40 rows (4 per rfp)
        self.assertEquals(40, len(self.parser.doc('#listingsResults table tbody tr')))

    def testParseList(self):
        self.parser.setup(self.parser.domain + self.parser.search_url + self.parser.search_variables)

        parsed_list = self.parser.parse_list()

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('rfpca', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.rfp.ca/display_rfp/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])

    def testNextWithoutDetails(self):
        # Parse without details
        parsed_list = self.parser.next(False)

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('rfpca', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.rfp.ca/display_rfp/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])

    def testNextWithDetails(self):
        # Parse with details
        parsed_list = self.parser.next()

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('rfpca', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.rfp.ca/display_rfp/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])
            self.assertNotEquals('', rfp['org'])
            self.assertNotEquals('', rfp['original_category'])
            self.assertNotEquals('', rfp['location'])
            self.assertNotEquals('', rfp['description'])
            self.assertTrue(isinstance(rfp['parsed_on'], datetime.date))
            self.assertTrue(isinstance(rfp['published_on'], datetime.date))
            self.assertTrue(isinstance(rfp['ends_on'], datetime.date))

    def testHasNext(self):
        self.assertTrue(self.parser.has_next())
        self.parser.search_variables = None
        self.assertFalse(self.parser.has_next())


class MerxParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = MerxParser()

    def testLoad(self):
        self.parser.load(self.parser.get_list_uri())

        # Make sure the PHPSESSID cookie is present
        #self.assertTrue(self.parser.headers['Cookie'].find('PHPSESSID=') != -1)

        # The request should exist now
        self.assertNotEquals(None, self.parser.request)

    def testParseList(self):
        self.parser.load(self.parser.get_list_uri())

        try:
            s = self.parser.request.read()
            self.parser.doc = pq( s )
        except lxml.etree.XMLSyntaxError as e:
            logging.error( 'Could not parse URI: %s' % self.list_uri )

        parsed_list = self.parser.parse_list()

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('merx', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.merx.com/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])


    def testNextWithoutDetails(self):
        # Parse without details
        parsed_list = self.parser.next(False)

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('merx', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.merx.com/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])
    
    def testNextWithDetails(self):
        # Parse with details
        parsed_list = self.parser.next()

        # 10 RFPs should have been parsed
        self.assertEquals(10, len(parsed_list))

        for rfp in parsed_list:
            self.assertEquals('merx', rfp['origin'])
            self.assertEquals(0, rfp['uri'].find('http://www.merx.com/'))
            self.assertNotEquals('', rfp['title'])
            self.assertNotEquals('', rfp['original_id'])
            self.assertNotEquals('', rfp['org'])
            self.assertNotEquals('', rfp['original_category'])
            self.assertNotEquals('', rfp['location'])
            self.assertNotEquals('', rfp['description'])
            self.assertTrue(isinstance(rfp['parsed_on'], datetime.date))
            self.assertTrue(isinstance(rfp['published_on'], datetime.date))
            self.assertTrue(isinstance(rfp['ends_on'], datetime.date))
    
    def testHasNext(self):
        self.assertTrue(self.parser.has_next())
        self.parser.page = -1
        self.assertFalse(self.parser.has_next())

if __name__ == '__main__':
    unittest.main()