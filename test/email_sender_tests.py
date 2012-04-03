from gaetestbed import MailTestCase
from backend.email import EmailSender
import unittest
from google.appengine.ext import testbed
from backend.models.rfp_entry import *
from backend.models.subscription import *
from datetime import date

str_email = 'john.sintal@gmail.com'


class EmailSenderTest(MailTestCase, unittest.TestCase):
    """
        Ensures that the actually sending of emails works.
    """

    def testEmailSent(self):
        emailSender = EmailSender()
        template_values = {
            "rfps": [],
            "name": 'test name',
            'search_text': 'test keyword',
            'is_admin': False,
            'search_uri': 'http://rfpow301.appspot.com/rfp/search/',
            'permalink_uri': 'http://rfpow301.appspot.com/rfp/'
        }

        emailSender.send(to=str_email, template_values=template_values)
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
        """
            The parsed date of rfp is newer than the last time the subscription was ran, so the
            emailer had not seen this rfp and thus must send it. So we deliberately
            have the email send the found RFP.
        """
        some_publish_date = date(2012, 11, 10) #date.today()

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        create_subscription("aUsername", "aKeyword1")

        sub = Subscription.all().fetch(2)[0]

        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)

        msg = "Found %d RFPs for %s with keyword '%s' for email: %s" % (1, sub.username, sub.keyword, str_email)

        self.assertEqual(1, len(res))
        self.assertEqual(res[0], msg)

    def testInvalidEmailSent(self):
        """
            The parsed date of rfp is older than the last time the subscription was ran, so it was
            likely that the emailer had already sent that old rfp out. So we deliberately
            have the email fail at find RFPs.
        """
        some_publish_date = date(1800, 11, 10) #date.today()

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)
        create_subscription("aUsername", "aKeyword1")

        sub = Subscription.all().fetch(2)[0]

        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)

        msg = "Found %d RFPs for %s with keyword '%s' for email: %s" % (1, sub.username, sub.keyword, str_email)

        self.assertEqual(1, len(res))
        self.assertNotEquals(res[0], msg)

    def testValidEmailSentMultipleRFPS(self):
        """
            The tests shows that multiple RFPs with the same keyword for the subscription are sent out.
            The email would list 2 rfps
            To add, the keywords are interchanged at different positions on the list.
        """
        some_publish_date = date(2012, 11, 10) #date.today()

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)

        create_RFP("aTitle2", "aDesc2", ["aKeyword2", "aKeyword1"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)


        create_subscription("aUsername", "aKeyword1")

        sub = Subscription.all().fetch(2)[0]

        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)

        msg = "Found %d RFPs for %s with keyword '%s' for email: %s" % (2, sub.username, sub.keyword, str_email)

        self.assertEqual(1, len(res))
        self.assertEquals(res[0], msg)


    def testInvalidEmailSentNORfps(self):
        """
            No Rfps are presented, thus an email should not be sent out.
        """
        some_publish_date = date(1800, 11, 10) #date.today()

#        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
#            some_publish_date, some_publish_date, some_publish_date)
        create_subscription("aUsername", "aKeyword1")

        sub = Subscription.all().fetch(2)[0]

        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)

        msg = 'No RFPs found for username: %s and keyword: %s' % (sub.username, sub.keyword)

        self.assertEqual(1, len(res))
        self.assertEquals(res[0], msg)


    def testInvalidEmailSentNOSubs(self):
        """
            No subscriptions are present, thus an email should not be sent out.
        """
        some_publish_date = date(1800, 11, 10) #date.today()

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
                    some_publish_date, some_publish_date, some_publish_date)
        #create_subscription("aUsername", "aKeyword1")


        res = list()

        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(None, "aFirstName", str_email, res)

        msg = 'Problem with sending a sub, probably None object'

        self.assertEqual(1, len(res))
        self.assertEquals(res[0], msg)

    def testInvalidEmailSentNOSubsAndNORfps(self):
        """
            No subscriptions/rfps are present, thus an email should not be sent out.
        """
        some_publish_date = date(1800, 11, 10) #date.today()
        res = list()
        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(None, "aFirstName", str_email, res)
        msg = 'Problem with sending a sub, probably None object'
        self.assertEqual(1, len(res))
        self.assertEquals(res[0], msg)

    def testInvalidEmailNoMatchKeys(self):
        """
            There exists subscriptions and
        """
        some_publish_date = date(1800, 11, 10) #date.today()
        some_publish_date = date(2012, 11, 10) #date.today()

        create_RFP("aTitle", "aDesc", ["aKeyword1", "aKeyword2"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)

        create_RFP("aTitle2", "aDesc2", ["aKeyword3", "aKeyword4"], "aOrg", "aURI", "aOrigID",
            some_publish_date, some_publish_date, some_publish_date)


        create_subscription("aUsername", "noMatchKeyword")
        sub = Subscription.all().fetch(2)[0]
        res = list()
        emailSender = EmailSender()
        emailSender._send_rfps_to_subscribers(sub, "aFirstName", str_email, res)
        msg = 'No RFPs found for username: %s and keyword: %s' % (sub.username, sub.keyword)
        self.assertEqual(1, len(res))
        self.assertEquals(res[0], msg)