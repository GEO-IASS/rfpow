import datetime
import logging
from google.appengine.ext import webapp

import RFP

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<html><body>')
        self.response.out.write('''
              <form action="/datastore/" method="post">
                  Title: <input type="text" name="title" />
                  <br/>
                  Description: <input type="text" name="description" />
                  <br/>
                  Organization: <input type="text" name="organization" />
                  <br/>
                  Original URI: <input type="text" name="original_uri" />
                  <br/>
                  Original ID: <input type="text" name="original_id" />
                  <br/>
                  Keywords(comma delimited): <input type="text" name="keywords" />
                  <br/>
                  <input type="submit" value="Create RFP"/>
              </form>

              <form action="/datastore/keyword" method="post">
                  Keyword: <input type="text" name="keyword" />
                  <br/>
                  <input type="submit" value="Query"/>
              </form>
              <form action="/datastore/query" method="post">
                  Query: <input type="text" name="query" />
                  <br/>
                  <input type="submit" value="Query"/>
              </form>
              ''')
    
    def post(self):
        RFP.create_RFP(self.request.get('title'),
            self.request.get('description'),
            self.request.get('keywords').split(','),
            self.request.get('organization'),
            self.request.get('original_uri'),
            self.request.get('original_id'),
            datetime.datetime.now().date(),
            datetime.datetime.now().date(),
            datetime.datetime.now().date())
        self.redirect('/datastore/')

class KeywordPage(webapp.RequestHandler):
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<html><body>RFPS<hr/>')
        rfps = RFP.query_RFPs_by_keyword(self.request.get('keyword'))

        for rfp in rfps:
            self.response.out.write('{0}: {1}<br/>{2}<br/>OrigID: {3}<br/>Org: {4}<br/>URI: {5}<br/>Keyword: {6}<hr/>'.format(rfp.title, rfp.description, rfp.publish_date, rfp.original_id, rfp.organization, rfp.original_uri, rfp.keywords))

class QueryPage(webapp.RequestHandler):
    
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<html><body>RFPS<hr/>')
        rfps = RFP.query_RFPs(self.request.get('query'))

        for rfp in rfps:
            self.response.out.write('{0}: {1}<br/>{2}<br/>OrigID: {3}<br/>Org: {4}<br/>URI: {5}<br/>Keyword: {6}<hr/>'.format(rfp.title, rfp.description, rfp.publish_date, rfp.original_id, rfp.organization, rfp.original_uri, rfp.keywords))


app = webapp.WSGIApplication([
  ('/datastore/', MainPage),
  ('/datastore/keyword', KeywordPage),
  ('/datastore/query', QueryPage)
], debug=True)
