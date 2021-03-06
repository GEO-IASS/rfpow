from webapp2_extras.routes import RedirectRoute
from handlers_user import *
from handlers_secured_main import *
from handlers_admin import *
from handlers_cron import *
import search

# Set up all controller routing. Doing this here instead of app.yaml lets us
# both solve the trailing slash problem and duplication of app instance code
_routes = [
    RedirectRoute('/login/', LoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout/', LogoutHandler, name='logout', strict_slash=True),
    RedirectRoute('/', HomePageHandler, name='secure', strict_slash=True),
    RedirectRoute(r'/rfp/search<format:(\.comet)?>/<search_query:.*>', RFPSearch, name='search', strict_slash=True),
    RedirectRoute(r'/rfp/list<format:(\.comet)?>', RFPList, name='list', strict_slash=True),
    RedirectRoute(r'/rfp<format:(\.comet)?>/<rfp_id:\d+>', RFPDetails, name='details', strict_slash=True),
    RedirectRoute(r'/rfp/subscribe/<keyword>', SubscribeHandler, name='subscribe', strict_slash=True),
    RedirectRoute(r'/rfp/unsubscribe/<keyword>', UnsubscribeHandler, name='unsubscribe', strict_slash=True),
    RedirectRoute('/rfp/email', AdminSendEmailHandler, name='email', strict_slash=True),
    RedirectRoute('/create-user/', CreateUserHandler, name='create-user', strict_slash=True),
    RedirectRoute('/edit-user/', EditUserHandler, name='edit-user', strict_slash=True),
    RedirectRoute('/create-rfp/', CreateRFPHandler, name='create-rfp', strict_slash=True),
    #RedirectRoute('/cron/merx', CronMerx, name='cron-merx', strict_slash=True),
    #RedirectRoute('/cron/rfpdotca', CronRfpdotca, name='cron-rfpdotca', strict_slash=True),
    #RedirectRoute('/cron/satender', CronSaTenders, name='cron-satender', strict_slash=True),
    RedirectRoute('/cron/email', CronSendEmail, name='email', strict_slash=True),
    RedirectRoute('/admin', AdminPanel, name='cron-merx', strict_slash=True),
    RedirectRoute('/searchindexing', search.SearchIndexing, name='searchindexing', strict_slash=True)

]

def get_routes():
    return _routes

def add_routes(app):
    for r in _routes:
        app.router.add(r)
