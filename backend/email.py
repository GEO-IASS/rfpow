from google.appengine.api import mail


class EmailSender:
    """
        EmailSender is responsible for gathering RFP data for each user who has subscribed to
        email updates, then sending that data via email.
    """


    def send(self, sender, subject, to, body):
        """
            Sends an email out based on the args given. Thin wrapper
            for Google's API.
        """

        message = mail.EmailMessage()
        message.sender = sender
        message.subject = subject
        message.to = to
        message.body = body
        message.send()

