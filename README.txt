# Production
Visit http://rfpow301.appspot.com/ for live demo of this webapp.

# Local development
To work on the app locally, you'll need Google's App Engine SDK:
    http://code.google.com/appengine/downloads.html

Aside from that, check out the project repo. Note that, if you use the GUI 
frontend for the SDK, it might require you to call the directory you check
out the repo into the same name as the app name, i.e. "rfpow301". 

To run the app, either add its directory in the frontend GUI, or, if you're on
a *nix OS, try using the `dev_appserver.py` script, like so:
    dev_appserver.py ~/path/to/rfpow301
	
# Structure
- /{root_dir}: controllers/handlers to frontend (communicate with view)
- /backend: services, more logic
- /backend/models: business models and their own logic
- /template: html files (view)
- /style: css related files
- /js: client side javascript code
- /routes.py: routing information given here, though some routing exist in the app.yaml

# Source Code/Snippet Credits
- Getting user management to work properly was helped by the using code found
here https://github.com/fredrikbonander/Webapp2-Sample-Applications
- Field forms used some CSS code from
http://stackoverflow.com/questions/7213787/unable-to-center-contents-of-a-fieldset
- http://www.javascriptkit.com/ for drop down month/year js code (this was heavily modified however)

# 3rd Party Libs
- jinja2, webapp2, and other libraries bundled with Google App Engine were utilized for building
the controllers and views of the application
- NDB: http://code.google.com/p/appengine-ndb-experiment/
- lxml (http://lxml.de/) and pyquery (http://pypi.python.org/pypi/pyquery) were used for parsing RFPs
- auth and sessions was used for user management (part of the webapp2_extras api)

# Notes:
- NDB folder is included in application due to a import statement in
webapp2_extras/appengine/auth/models.py
