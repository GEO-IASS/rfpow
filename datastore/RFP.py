import logging
from google.appengine.ext import db

class RFP(db.Model):
	publish_date = db.DateProperty()
	close_date = db.DateProperty()
	title = db.StringProperty()
	description = db.TextProperty()
	keywords = db.StringListProperty()


def create_RFP(title, description, publish_date, close_date, keywords):
	rfp = RFP()

	rfp.title = title
	rfp.description = description
	rfp.publish_date = publish_date
	rfp.close_date = close_date
	rfp.keywords = keywords

	rfp.put()

def query_RFPs(keyword):
	return RFP.gql("WHERE keywords = '{0}'".format(keyword))