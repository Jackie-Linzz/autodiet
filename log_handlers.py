import tornado.web
import uuid

from tornado.escape import json_decode, json_encode


import mydata
import mydatabase


class EntryHandler(tornado.web.RequestHandler):
    def get(self):
        # session , if exists use current and set expire time
        session = self.get_secure_cookie('session', None)
        self.clear_all_cookies()

        if session is None:
            # if not exists, set new one
            uid = str(uuid.uuid4())
            self.set_secure_cookie('session', uid)
        else:
            self.set_secure_cookie('session', session, expires_days=60)
        self.render('index.html')

    def post(self):
        #as customer
        self.set_secure_cookie('who', 'customer')
        #set desk
        desk = json_decode(self.get_argument('desk')).upper()
        if mydatabase.check_desk(desk):
            self.set_cookie('desk', desk)
            if desk not in mydata.discussion or mydata.discussion[desk] is None:
                mydata.discussion[desk] = mydata.DeskOrder(desk)
            if desk not in mydata.discussion_waiters:
                mydata.discussion_waiters[desk] = set()

            response = {'status': 'ok', 'next': '/customer-category'}
            self.write(json_encode(response))
        else:
            response = {'status': 'ok', 'next': '/'}
            self.write(json_encode(response))


class FacultyLoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('faculty-login.html')

    def post(self):
        fid = self.get_argument('name', None)
        password = self.get_argument('password', None)
        if fid is None or password is None:
            response = {'status': 'error', 'next': '/faculty-login'}
            self.finish(json_encode(response))
            return
        fid = json_decode(fid)
        password = json_decode(password)
        faculty = mydatabase.get_faculty()
        faculty = filter(lambda x: x['id'] == fid, faculty)
        row = None
        if faculty:
            row = faculty[0]
        response = {'status': 'error', 'next': '/faculty-login'}
        if row:
            if password == row['password']:
                who = row['role']
                mydata.init_role(fid)
                self.set_secure_cookie('who', who)
                self.set_secure_cookie('fid', fid)
                response = {'status': 'ok', 'next': '/faculty-home'}

        self.finish(json_encode(response))


class FacultyHomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('faculty-home.html')

    def post(self):
        who = self.get_secure_cookie('who')
        response = {}
        if who == 'waiter':
            response = {'status': 'ok', 'next': '/waiter-request'}
        elif who == 'cook':
            width = json_decode(self.get_argument('screenWidth'))
            if width > 800:
                response = {'status': 'ok', 'next': '/cook-cook-pad'}
            else:
                response = {'status': 'ok', 'next': '/cook-cook-phone'}
        elif who == 'manager':
            response = {'status': 'ok', 'next': '/manager'}
        self.write(json_encode(response))


class FacultyLogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie('who')
        self.clear_cookie('fid')
        response = {'status': 'ok', 'next': '/'}
        self.finish(json_encode(response))