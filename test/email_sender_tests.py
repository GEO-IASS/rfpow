import unittest
from gaetestbed import MailTestCase
from backend.email import EmailSender

class MyTestCase(MailTestCase, unittest.TestCase):

    def test_email_sent(self):
        emailSender = EmailSender()
        str_email = 'rfpdemo301@gmail.com'
        template_values = {
            "rfps" : [],
            "name" : 'test name',
            'search_text' : 'test keyword',
            'is_admin' : False,
            'search_uri': 'http://rfpow301.appspot.com/rfp/search/',
            'permalink_uri': 'http://rfpow301.appspot.com/rfp/'
        }

        emailSender.send( to=str_email, template_values=template_values)
        self.assertEmailSent(str_email, template_values)
        self.assertEqual(len(self.get_sent_messages()), 1)