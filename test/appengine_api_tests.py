from google.appengine.api import urlfetch
import unittest



class AppEngineAPITest(unittest.TestCase):

    def test_urlfetch(self):
        response = urlfetch.fetch('http://www.google.com')
        self.assertEquals(0, response.content.find('<html>'))

    def test_wewfe(self):
        self.assertEquals(0, 1)




