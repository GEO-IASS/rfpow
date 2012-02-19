import webapp2
import lxml
from pyquery import PyQuery as pq

class MainPage(webapp2.RequestHandler):
  def get(self):
      # grab a page with RFP results
      d = pq(url="http://www.merx.com/English/SUPPLIER_Menu.asp?WCE=ButtonClick&TAB=1&PORTAL=MERX&State=2&revision=&hcode=D6wWmddGRBZUCi03zMrw7w%3d%3d")
      rows = d(".BoxBody_Center.FullSearchListBody_Center table tr")

      # remove title row
      rows.pop(0)

      result = u"Latest RFPs: \n"
      for i in range(2, len(rows)-1):
          title = rows.eq(i).find('td').eq(5).find('a')
          result = result + str(i)+". "+title.text() + "\n" 

      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write( result )

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
