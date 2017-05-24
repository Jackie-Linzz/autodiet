import tornado.web
import time
import uuid
import functools

from tornado.escape import json_decode, json_encode

import mydata


def cook_auth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        who = self.get_secure_cookie('who', None)

        #desk should in reasonable range, here is a simple check
        if who != 'cook':
            response = {'status': 'denied', 'next': '/'}
            self.finish(json_encode(response))
            return

        return method(self, *args, **kwargs)
    return wrapper

#used for data handler
class CookCookHandler(tornado.web.RequestHandler):
    def get(self):

        #if id exists, clear uid
        #self.set_secure_cookie('uid', str(uuid.uuid4()))
        self.render('cook-cook.html')
    @cook_auth
    def post(self):
        fid = self.get_secure_cookie('fid')
        mycook = mydata.get_mycook(fid)
        response = {'status': 'ok', 'mycook': mycook}
        self.write(json_encode(response))


class CookCookPadHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('cook-cook-pad.html')


class CookCookOtherPadHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('cook-cook-other-pad.html')


class CookCookPhoneHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('cook-cook-phone.html')


class CookCookOtherPhoneHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('cook-cook-other-phone.html')


class CookInstructionHandler(tornado.web.RequestHandler):
    @cook_auth
    def post(self):
        fid = self.get_secure_cookie('fid')
        ins = json_decode(self.get_argument('instruction'))
        mycook = mydata.cook_perform(fid, ins)
        response = {'status': 'ok', 'mycook': mycook}
        self.write(json_encode(response))


class CookCallHandler(tornado.web.RequestHandler):

    def post(self):
        fid = self.get_secure_cookie('fid')
        mydata.cook_requests.request(fid)
        response = {'status': 'ok'}
        self.finish(json_encode(response))


class CookCookUpdateHandler(tornado.web.RequestHandler):

    def post(self):
        pass


