import time
import logging
from backend.parsers import MerxParser
from backend.datastore import RFP

class ScheduledParse():
    """A class for a task of parsing various websites. Run by cron"""

    @staticmethod
    def parse(parser, ignore_duplicates=False, start_id=None, 
            stop_on_dupe=False, limit=None):
        """Parse a bunch of RFPs from Merx and stash results in the DB
        
        parser -- instance of a Parser class with which to parse
        ignore_duplicates -- save RFP even if already in the DB
        start_id -- begin parsing at original_id == start_id
        stop_on_dupe -- halt parse job if we hit a duplicate
        limit -- parse at most `limit` jobs
        """

        parsed_total = 0
        parsed_new = 0
        page = 0

        # skip RFPs until found given start_id. Handy for resuming a parse job
        skip = start_id is not None

        while parser.has_next():
            page += 1
            rfps = parser.next(parse_each=False)
            parsed_total = parsed_total + len(rfps)

            for r in rfps:
                title = r['title'].encode('utf-8')
                # skip if given an ID to resume parsing from
                if skip: 
                    if start_id != r['original_id']:
                        logging.info( 'Skipping while waiting for %d: %s' % (start_id, title) )
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
                           logging.info( 'Stopping early on RFP: %s' % title )
                           return (parsed_total, parsed_new)
                       else:
                           logging.info( 'Skipping existing RFP: %s.' % title )
                           continue

                   else:
                       # stop early if there's a limit on number of RFPs parsed
                       if limit is not None and limit <= parsed_new:
                           logging.info( 'Stopping early due to limit: %s' % title )
                           return (parsed_total, parsed_new)

                       rfp = RFP.from_dict( parser.parse_details(r) )
                       rfp.put()
                       rfp.index()
                       parsed_new += 1

                logging.info( u'Saving new RFP: %s' % rfp )
            logging.info( 'Parsed page %d of Merx results' % page )

        return (parsed_total, parsed_new)
