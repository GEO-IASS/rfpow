import webapp2
from handlers_cron import CronSendEmail, CronRfpdotca, CronSaTenders, CronMerx
from handlers_secured_main import CreateRFPHandler
import routes

webapp2_config = {}
webapp2_config['webapp2_extras.sessions'] = {
    'secret_key': '6023a964-ea67-4965-b8c1-8b098b87a51a',
    }

# Putting admin routes here since Webapp2 Extra doesn't provide admin login restrictions
# Refer to app.yaml for related routes
admin_routes =  [('/create-rfp/', CreateRFPHandler),
                ('/rfp/email', CronSendEmail),
                ('/cron/merx', CronMerx),
                ('/cron/rfpdotca', CronRfpdotca),
                ('/cron/satender', CronSaTenders)
                ]
app = webapp2.WSGIApplication(config=webapp2_config, routes=admin_routes)
routes.add_routes(app)
