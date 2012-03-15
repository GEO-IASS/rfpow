class RFPowUser():
    def __init__(self, post_data):
        self.username = post_data.get('username')
        self.password = post_data.get('password')
        self.first_name = post_data.get('first_name')
        self.last_name = post_data.get('last_name')
        self.cc_number = post_data.get('cc_number')
        self.name_on_cc = post_data.get('name_on_cc')
        self.expiry_date = post_data.get('expiry_date_month') + "," + post_data.get('expiry_date_year')
        self.email = post_data.get('email')
        # str_keywords =  post_data.POST.get('keywords')
        #        list_keywords = []
        #        for x in str_keywords.split(','):
        #            list_keywords.append(x.strip())


    def __str__(self):
        return self.username

    def update(self, db_user):
        #db_user[0].username = self.username
        db_user[0].password_raw = self.password
        db_user[0].first_name = self.first_name
        db_user[0].last_name = self.last_name
        db_user[0].cc_number = self.cc_number
        db_user[0].name_on_cc = self.name_on_cc
        db_user[0].expiry_date = self.expiry_date
        db_user[0].email = self.email
        db_user[0].put()

