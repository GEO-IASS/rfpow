import logging
from google.appengine.ext import db

class RFP(db.Model):
	title = db.StringProperty()
	description = db.TextProperty()
	keywords = db.StringListProperty()
	organization = db.StringProperty()
	original_uri = db.StringProperty()
	original_id = db.StringProperty()
	publish_date = db.DateProperty()
	parse_date = db.DateProperty()
	close_date = db.DateProperty()


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