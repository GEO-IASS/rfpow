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
    """
        Adds a subscription to the datastore, storing the username of the user
        who subscribed to the keyword for updates via email. An old date is given
        to the subscription's last_updated so we ensure all rfps are given on the first
        update.

        If there's already a subscription with the same username and keyword, then return
        False, else True.
    """

    if (does_sub_exist(username, keyword)):
        return False
    else:
        subscription = Subscription()
        subscription.username = username
        subscription.keyword = keyword
        subscription.last_updated = date.fromordinal(730920) # some very old date (2002-03-11)
        subscription.put()
        return True


def does_sub_exist(username, keyword):
    """
        Return sub (subscription) already exists
    """

    return Subscription.gql("WHERE keyword = :1 AND username = :2",
        keyword, username).get() is not None

