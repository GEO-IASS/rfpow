import logging
from datetime import datetime
from google.appengine.ext import db

class RFP(db.Model):
    title = db.StringProperty()
    description = db.TextProperty()
    keywords = db.StringListProperty()
    organization = db.StringProperty()
    original_uri = db.StringProperty()
    original_id = db.StringProperty()
    origin = db.StringProperty()
    publish_date = db.DateProperty()
    parse_date = db.DateProperty()
    close_date = db.DateProperty()

    @classmethod
    def from_dict( self, dict ):
        """Create an RFP based on a dictionary as received from a parser"""
        rfp = RFP()

        rfp.title = dict['title']
        rfp.description = dict['description']
        rfp.keywords = [dict['original_category']]
        rfp.organization = dict['org']
        rfp.original_uri = dict['uri']
        rfp.original_id = dict['original_id']
        rfp.origin = dict['origin']
        # XXX: parse dates properly
        rfp.publish_date = datetime.strptime(dict['published_on'], '%Y-%m-%d')
        rfp.parse_date = datetime.now()
        #rfp.close_date = close_date

        return rfp

    @classmethod
    def by_original_id(self, origin, id):
        return RFP.gql("WHERE original_id = :1", id)
    
    def __str__(self):
        return u"<RFP Object: '%s'>" % self.title


def create_RFP(title, description, keywords, organization, original_uri, original_id, publish_date, parse_date, close_date):
    rfp = RFP()

    rfp.title = title
    rfp.description = description
    rfp.keywords = keywords
    rfp.organization = organization
    rfp.original_uri = original_uri
    rfp.original_id = original_id
    rfp.publish_date = publish_date
    rfp.parse_date = parse_date
    rfp.close_date = close_date
    
    rfp.put()

def query_RFPs_by_keyword(keyword):
    return RFP.gql("WHERE keywords = '{0}'".format(keyword))

def query_RFPs(query):
    return RFP.gql(query)


