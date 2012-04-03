Run this script to run a lite SMPT server that handles emails (for local development).

For John's Reference, he runs this:
	"C:\Python27\python.exe" "C:\Users\John\Desktop\Group_E\email_server\smtps.py" 9989

And adds this to his config when running GAE server:
	--smtp_host=localhost --smtp_port=9989125952

Note: This is NOT required to run for running http://localhost:<port>/test