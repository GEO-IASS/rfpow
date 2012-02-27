from backend.datastore import RFP

class ScheduledParse():
    """A class for a task of parsing various websites. Run by cron"""

    @staticmethod
    def parse_merx():
        """Parse a bunch of RFPs from Merx and stash results in the DB"""
        rfp = RFP()

        rfp.title = "Hello"
        rfp.description = 'test'
        
        rfp.put()
