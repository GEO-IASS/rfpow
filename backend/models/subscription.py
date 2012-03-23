from google.appengine.ext import db
from datetime import datetime
from datetime import date

class Subscription(db.Model):
    """
        Holds info regarding what RFPs some user has requested to be notified via email on.
    """
    username = db.StringProperty()
    keyword = db.StringProperty()
    last_updated = db.DateProperty()

def create_subscription(username, keyword):
    subscription = Subscription()
    subscription.username = username
    subscription.keyword = keyword
    subscription.last_updated = date.fromordinal(730920) # some very old date (2002-03-11)
    subscription.put()



