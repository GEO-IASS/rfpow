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
                  Keywords(comma delimited): <input type="text" name="keywords" />
                  <br/>
                  <input type="submit" value="Create RFP"/>
              </form>

              <form action="/datastore/query" method="post">
                  Keyword: <input type="text" name="keyword" />
                  <br/>
                  <input type="submit" value="Query"/>
              </form>
              ''')
    
    def post(self):
        RFP.create_RFP(self.request.get('title'),
            self.request.get('description'),
            datetime.datetime.now().date(),
            datetime.datetime.now().date(),
            self.request.get('keywords').split(','))
        self.redirect('/datastore/')

class QueryPage(webapp.RequestHandler):
    
  def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<html><body>RFPS<hr/>')
        rfps = RFP.query_RFPs(self.request.get('keyword'))

        for rfp in rfps:
            self.response.out.write('{0}: {1}<br/>{2}<br/>{3}<hr/>'.format(rfp.title, rfp.description, rfp.publish_date, rfp.keywords))

    




app = webapp.WSGIApplication([
  ('/datastore/', MainPage),
  ('/datastore/query', QueryPage)
], debug=True)
