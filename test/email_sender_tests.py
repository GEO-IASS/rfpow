import unittest
from gaetestbed import MailTestCase
from backend.email import EmailSender
import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
from backend.models.rfp_entry import *
from backend.models.subscription import *
str_email = 'john.sintal@gmail.com'


class EmailSenderTest(MailTestCase, unittest.TestCase):
    """
        Ensures that the actually sending of emails works.
    """

    def testEmailSent(self):

        emailSender = EmailSender()
        template_values = {
            "rfps" : [],
            "name" : 'test name',
            'search_text' : 'test keyword',
            'is_admin' : False,
            'search_uri': 'http://rfpow301.appspot.com/rfp/search/',
            'permalink_uri': 'http://rfpow301.appspot.com/rfp/'
        }

        emailSender.send( to=str_email, template_values=template_values)
        self.assertEmailSent(to=str_email)


class EmailDatastoreTest(MailTestCase, unittest.TestCase):
    """
        Ensures that the correct models, datastore and sending all work together.
    """

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testValidEmailSent(self):
        default_date_sub = 530920

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            date.fromordinal(default_date_sub), date.fromordinal(default_date_sub), date.fromordinal(default_date_sub) )
        create_subscription("aUsername", "aKeyword1")

        sub = Subscription.all().fetch(2)[0]
        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)

        msg = "Found %d RFPs for %s with keyword '%s' for email: %s" % (1, sub.username, sub.keyword, str_email)

        self.assertEqual(1, len(res))
        self.assertEqual(res[0], msg)
