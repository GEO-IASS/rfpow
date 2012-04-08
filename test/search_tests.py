from gaetestbed import MailTestCase
from backend.email import EmailSender
from backend.models.rfp_entry import *
import unittest
from google.appengine.ext import testbed
from backend.models.rfp_entry import *
from backend.models.subscription import *
from datetime import date

class SearchTest(MailTestCase, unittest.TestCase):
    '''
    Ensures the search funcion is working.
    '''

    def testSearch(self):
        '''
        Test basic search function.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("ThisisauniqueTitle1", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("ThisisauniqueTitle1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "ThisisauniqueTitle1")        
                
    def testSearchFutureDate(self):
        '''
        Test searching a rfp entry providing a future parse date while searching.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("ThisisauniqueTitle2", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("ThisisauniqueTitle2", date=date(2012, 12, 10))
        self.assertEqual(len(result), 0)        
        
    def testSearchOldDate(self):
        '''
        Test searching a rfp entry providing an old parse date while searching.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("ThisisauniqueTitle3", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("ThisisauniqueTitle3", date = date(1999, 9, 9))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "ThisisauniqueTitle3")        
        
    def testSearchLimit(self):
        '''
        Test search function when providing a limit of results returned.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("haoran 1", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        create_RFP("haoran 2", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        create_RFP("haoran 3", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("haoran", limit = 2)
        self.assertEqual(len(result), 2)
        
    def testSearchKeys(self):
        '''
        Test if result is returned correctly when passing keys_only argument
        while searching, where a list of tuple should be returned.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("ThisisauniqueTitle3", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("ThisisauniqueTitle3", keys_only = True)
        self.assertEqual(type(result[0]), tuple)
        
    def testSearchMultiWord(self):
        '''
        Test search function of searching phrases instead of a single word.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP("this is a unique testerssssss", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search("unique testerssssss")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "this is a unique testerssssss")
        
    def testSearchUnicode(self):
        '''
        Test search function for unicode support.
        '''
        
        some_publish_date = date(2012, 11, 10)
        create_RFP(u"testerssss", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        result = RFP.search(u"testerssss")
        self.assertEqual(result[0].title, u"testerssss")