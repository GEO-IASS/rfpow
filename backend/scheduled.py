import time
import logging
from backend.parsers import MerxParser
from backend.datastore import RFP

class ScheduledParse():
    """A class for a task of parsing various websites. Run by cron"""

    @staticmethod
    def parse_merx():
        """Parse a bunch of RFPs from Merx and stash results in the DB"""

        # XXX: Run MerxParser in a loop a fixed number of times (say 50)
        # and save results to DB. Keep in mind script runtime is limited
        # to 10 minutes

        # do 50 RFPs to start
        parser = MerxParser()
        parsed_total = 0

        for i in range(5):
            rfps = parser.next()

            for r in rfps:
                rfp = RFP.from_dict(r)

                # check if we've parsed this RFP before
                if RFP.by_original_id( r['origin'], r['original_id'] ).count() != 0:
                    logging.info( 'Reached existing RFP, stopping: %s' % rfp )
                    return parsed_total

                logging.info( u'Saving new RFP: %s' % rfp )
                rfp.put()
            time.sleep(3)
            parsed_total = parsed_total + len(rfps)

        return parsed_total
