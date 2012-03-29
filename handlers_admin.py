import webapp2
import jinja2
import os
import logging
import backend.parsers as parsers
from backend.scheduled import ScheduledParse
from handlers_base import *

class AdminParser(BaseHandler, HTMLRenderer):
    """Controller for the parser section of the admin panel"""

    @user_required 
    @admin_required
    def get(self, status=None):
        # now stash results into a dict and use it in the top_rfps.html template
        template_data = {}
        
        if status is not None: 
            template_data['status'] = status
        self.show_rendered_html('templates/admin_parsers.html', template_data)

    @user_required
    def post(self):
        """Used to set parser settings and trigger parsers"""
        parser_name = self.request.get('parser')
        ignore_duplicates = self.request.get('ignore_duplicates')
        start_id = self.request.get('start_id')
        stop_on_dupe = self.request.get('stop_on_dupe')
        limit = self.request.get('parse_limit')

        if parser_name == 'merx':
            parser = parsers.MerxParser()
        elif parser_name == 'rfp.ca':
            parser = parsers.RFPParser()
        elif parser_name == 'satender':
            parser = parsers.STParser()
        (parsed, new) = ScheduledParse.parse( 
                parser,
                ignore_duplicates is not '',
                (start_id is not "") and start_id or None,
                stop_on_dupe is not '',
                (limit is not "") and int(limit.strip()) or None )

        self.get( '%d RFPs parsed, %d new stored. See logs.' % (parsed, new) )

