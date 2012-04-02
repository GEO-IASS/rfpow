from google.appengine.ext import db
from datetime import datetime
from datetime import date
import logging


class Subscription(db.Model):
    """
        Holds info regarding what RFPs some user has requested to be notified via email.
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

    if (sub_exists(username, keyword)):
        return False
    else:
        subscription = Subscription()
        subscription.username = username
        subscription.keyword = keyword
        subscription.last_updated = date.fromordinal(730920) # some very old date (2002-03-11)
        subscription.put()
        return True

def remove_subscription(username, keyword):
    """
        Remove a subscription from the datastore

        If there is no subscription with the same username and keyword, then return
        False, else True.
    """

    if (not sub_exists(username, keyword)):
        return 0
    else:
        q = db.GqlQuery("SELECT * FROM Subscription WHERE keyword = :1 AND username = :2", keyword, username)
        subs = q.fetch(100)

        # Should never exceed more than one subscriptions since we (keyword, username) is a unique key constraint
        if (len(subs) > 1):
            logging.critical("Deleting more than one subscriptions for key (%s, %s) " % username, keyword)

        for sub in subs:
            sub.delete()


        return len(subs)


def sub_exists(username, keyword):
    """
        Return sub (subscription) if it exists based on username and keyword, otherwise
        return None.
    """

    return Subscription.gql("WHERE keyword = :1 AND username = :2",
        keyword, username).get() is not None

