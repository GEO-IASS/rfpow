import time
import logging
from backend.parsers import MerxParser
from backend.datastore import RFP

class ScheduledParse():
    """A class for a task of parsing various websites. Run by cron"""

    @staticmethod
    def parse_merx(ignore_duplicates, start_id=None):
        """Parse a bunch of RFPs from Merx and stash results in the DB"""

        # XXX: Run MerxParser in a loop a fixed number of times (say 50)
        # and save results to DB. Keep in mind script runtime is limited
        # to 10 minutes

        # do 50 RFPs to start
        parser = MerxParser()
        parsed_total = 0
        page = 0
        # skip RFPs until found given start_id. Handy for resuming a parse job
        skip = start_id is not None

        while parser.has_next():
            page += 1
            rfps = parser.next()

            for r in rfps:
                rfp = RFP.from_dict(r)

                # skip if given an ID to resume parsing from
                if skip: 
                    if start_id != r['original_id']:
                        logging.info( 'Skipping: %s' % rfp )
                        continue
                    else:
                        skip = False
                        logging.info( 'Resuming parsing from ID: %s' % r['original_id'] )

                # check if we've parsed this RFP before
                if not ignore_duplicates and \
                   RFP.by_original_id( r['origin'], 
                           r['original_id'] ).count() != 0:
                    logging.info( 'Skipping existing RFP: %s' % rfp )
                    continue

                logging.info( u'Saving new RFP: %s' % rfp )
                rfp.put()
            logging.info( 'Parsed page %d of Merx results' % page )
            time.sleep(3)
            parsed_total = parsed_total + len(rfps)

        return parsed_total
