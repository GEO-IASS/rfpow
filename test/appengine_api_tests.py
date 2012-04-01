import unittest
from google.appengine.api import urlfetch
import unittest
import logging
from google.appengine.ext import db
import model


class AppEngineAPITest(unittest.TestCase):

    def test_urlfetch(self):
        response = urlfetch.fetch('http://www.google.com')
        self.assertEquals(0, response.content.find('<html>'))

    def test_wewfe(self):
        self.assertEquals(0, 1)

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Populate test entities.
        entity = model.MyEntity(name='Bar')
        self.setup_key = entity.put()

    def tearDown(self):
        # There is no need to delete test entities.
        pass

    def test_new_entity(self):
        entity = model.MyEntity(name='Foo')
        self.assertEqual('Foo', entity.name)

    def test_saved_enitity(self):
        entity = model.MyEntity(name='Foo')
        key = entity.put()
        self.assertEqual('Foo', db.get(key).name)

    def test_setup_entity(self):
        entity = db.get(self.setup_key)
        self.assertEqual('Bar', entity.name)


