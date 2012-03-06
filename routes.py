from webapp2_extras.routes import RedirectRoute
from handlers_user import *
from handlers_controlpanel import *
from handlers_admin import *
from handlers_cron import *

# Set up all controller routing. Doing this here instead of app.yaml lets us
# both solve the trailing slash problem and duplication of app instance code
_routes = [
    RedirectRoute('/login/', LoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout/', LogoutHandler, name='logout', strict_slash=True),
    RedirectRoute('/', HomePageHandler, name='secure', strict_slash=True),
    RedirectRoute('/secure', HomePageHandler, name='secure', strict_slash=True),
    RedirectRoute('/create-user/', CreateUserHandler, name='create-user', strict_slash=True),
    RedirectRoute('/top-rfps/', TopRFPSHandler, name='top-rfps', strict_slash=True),
    RedirectRoute('/query/', QueryRFPHandler, name='query', strict_slash=True),
    RedirectRoute('/create-rfp/', CreateRFPHandler, name='create-rfp', strict_slash=True),
    RedirectRoute('/view-kw-results/', KeywordResultsHandler, name='view-kw-results', strict_slash=True),
    RedirectRoute('/view-query-results/', QueryResultsHandler, name='view-query-results', strict_slash=True),
    RedirectRoute('/cron/merx', CronMerx, name='cron-merx', strict_slash=True),
    RedirectRoute('/admin', AdminParser, name='cron-merx', strict_slash=True),
    RedirectRoute('/list-keywords', ListKeywordsHandler, name='list-keywords', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    for r in _routes:
        app.router.add(r)
