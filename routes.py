from webapp2_extras.routes import RedirectRoute
from handlers_user import LoginHandler
from handlers_user import LogoutHandler
from handlers_user import SecureRequestHandler
from handlers_user import CreateUserHandler
from handlers_controlpanel import TopRFPSHandler
from handlers_controlpanel import QueryResultsHandler
from handlers_controlpanel import KeywordResultsHandler
from handlers_controlpanel import CreateAndQueryRFPHandler



# Using redirect route instead of simple routes since it supports strict_slash
# Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
# RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute

_routes = [
    RedirectRoute('/login/', LoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout/', LogoutHandler, name='logout', strict_slash=True),
    RedirectRoute('/', SecureRequestHandler, name='secure', strict_slash=True),
    RedirectRoute('/secure', SecureRequestHandler, name='secure', strict_slash=True),
    RedirectRoute('/create-user/', CreateUserHandler, name='create-user', strict_slash=True),
    RedirectRoute('/top-rfps/', TopRFPSHandler, name='top-rfps', strict_slash=True),
    RedirectRoute('/create-rfp/', CreateAndQueryRFPHandler, name='create-rfp', strict_slash=True),
    RedirectRoute('/view-kw-results/', KeywordResultsHandler, name='view-kw-results', strict_slash=True),
    RedirectRoute('/view-query-results/', QueryResultsHandler, name='view-query-results', strict_slash=True),
]

def get_routes():
    return _routes


def add_routes(app):
    for r in _routes:
        app.router.add(r)
