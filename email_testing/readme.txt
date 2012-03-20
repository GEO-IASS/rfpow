Run this script to run a lite SMTP server that handles emails (for local development).

For John's Reference, he runs this:
	"C:\Python27\python.exe" "C:\Users\John\Desktop\Group_E\email_testing\smtps.py" 9989

And adds this to his config when running GAE server:
	--smtp_host=localhost --smtp_port=9989