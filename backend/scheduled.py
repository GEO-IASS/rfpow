import time
import logging
from backend.parsers import MerxParser
from backend.datastore import RFP

class ScheduledParse():
    """A class for a task of parsing various websites. Run by cron"""

    @staticmethod
    def parse_merx(ignore_duplicates, start_id=None, stop_on_dupe=False,
            limit=None):
        """Parse a bunch of RFPs from Merx and stash results in the DB"""

        parser = MerxParser()
        parsed_total = 0
        parsed_new = 0
        page = 0

        # skip RFPs until found given start_id. Handy for resuming a parse job
        skip = start_id is not None

        while parser.has_next():
            page += 1
            rfps = parser.next()
            parsed_total = parsed_total + len(rfps)

            for r in rfps:
                rfp = RFP.from_dict(r)

                # skip if given an ID to resume parsing from
                if skip: 
                    if start_id != r['original_id']:
                        logging.info( 'Skipping while waiting for %d: %s' % (start_id, rfp) )
                        continue
                    else:
                        skip = False
                        logging.info( 'Resuming parsing from ID: %s' % r['original_id'] )

                # check if we've parsed this RFP before
                if not ignore_duplicates:
                   db_match = RFP.by_original_id( r['origin'], r['original_id'] )
                   
                   # either skip if this RFP is already parsed, or stop parsing
                   if db_match.count() != 0:
                       if stop_on_dupe:
                           logging.info( 'Stopping early on RFP: %s' % rfp )
                           return (parsed_total, parsed_new)
                       else:
                           logging.info( 'Skipping existing RFP: %s.' % rfp )
                           continue

                   else:
                       # stop early if there's a limit on number of RFPs parsed
                       if limit is not None and limit <= parsed_new:
                           logging.info( 'Stopping early due to limit: %s' % rfp )
                           return (parsed_total, parsed_new)

                       parsed_new += 1

                logging.info( u'Saving new RFP: %s' % rfp )
                rfp.put()
            logging.info( 'Parsed page %d of Merx results' % page )
            time.sleep(3)

        return (parsed_total, parsed_new)
