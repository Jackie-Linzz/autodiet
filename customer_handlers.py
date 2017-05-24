import tornado.web
import tornado.gen
import functools
from tornado.escape import json_decode, json_encode

import mydata
import mydatabase


def customer_auth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        who = self.get_secure_cookie('who', None)
        desk = self.get_cookie('desk', None)
        #desk should in reasonable range, here is a simple check
        if who != 'customer':
            response = {'status': 'denied', 'next': '/'}
            self.finish(json_encode(response))
            return
        if desk not in mydatabase.desks:
            response = {'status': 'denied', 'next': '/'}
            self.finish(json_encode(response))
            return
        return method(self, *args, **kwargs)
    return wrapper


# for customer-category
class CustomerCategoryHandler(tornado.web.RequestHandler):
    @customer_auth
    def get(self):
        self.clear_cookie('cid')
        self.render('customer-category.html')

    def post(self):
        desk = self.get_cookie('desk')
        categories = mydata.categories

        myorder = mydata.get_discussion_order(desk)
        response = {'status': 'ok', 'categories': categories, 'myorder': myorder}
        self.finish(json_encode(response))


class CustomerCategoryLogoutHandler(tornado.web.RequestHandler):

    def post(self):
        self.clear_cookie('desk')
        response = {'status': 'ok', 'next': '/'}
        self.finish(json_encode(response))


class CustomerCategoryTransferHandler(tornado.web.RequestHandler):

    def post(self):
        cid = json_decode(self.get_argument('category'))
        self.set_cookie('cid', str(cid))
        response = {'status': 'ok', 'next': '/customer-detail'}
        self.finish(json_encode(response))
        return


class CustomerCategoryRequestHandler(tornado.web.RequestHandler):

    def post(self):
        desk = self.get_cookie('desk')
        mydata.customer_requests.request(desk)
        response = {'status': 'ok'}
        self.finish(json_encode(response))
        return


class CustomerMakeOrderHandler(tornado.web.RequestHandler):

    def post(self):
        who = self.get_secure_cookie('who')
        desk = self.get_cookie('desk')
        ins = json_decode(self.get_argument('instruction'))
        myorder = mydata.discussion_perform(desk, who, ins)

        response = {'status': 'ok', 'myorder': myorder}
        self.finish(json_encode(response))


class CustomerOrderUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    @customer_auth
    def post(self):
        desk = self.get_cookie('desk')
        stamp = json_decode(self.get_argument('stamp'))
        myorder = yield mydata.discussion_order_update(desk, stamp)
        response = {'status': 'ok', 'myorder': myorder}
        self.finish(json_encode(response))
        raise tornado.gen.Return()


class CustomerDetailHandler(tornado.web.RequestHandler):
    @customer_auth
    def get(self):
        self.clear_cookie('item_id')
        self.render('customer-detail.html')

    def post(self):
        desk = self.get_cookie('desk')
        cid = int(self.get_cookie('cid'))
        myorder = mydata.get_discussion_order(desk)
        diet = mydata.diet
        categories = mydata.categories
        response = {'status': 'ok', 'myorder': myorder, 'diet': diet, 'categories': categories, 'cid': cid}
        self.finish(json_encode(response))


class CustomerDetailTransferHandler(tornado.web.RequestHandler):

    def post(self):
        print self.request.query_arguments
        item_id = json_decode(self.get_argument('item_id'))
        self.set_cookie('item_id', str(item_id))
        response = {'status': 'ok', 'next': '/customer-overlay?hh=0'}
        self.finish(json_encode(response))
        return


class CustomerOverlayHandler(tornado.web.RequestHandler):
    @customer_auth
    def get(self):
        self.render('customer-overlay.html')

    def post(self):
        item_id = int(self.get_cookie('item_id'))
        cid = int(self.get_cookie('cid'))
        desk = self.get_cookie('desk')
        myorder = mydata.get_discussion_order(desk)
        diet = mydata.diet
        response = {'status': 'ok', 'myorder': myorder, 'diet': diet, 'cid': cid, 'item_id': item_id}
        self.finish(json_encode(response))


class CustomerOrderHandler(tornado.web.RequestHandler):
    @customer_auth
    def get(self):
        session = self.get_secure_cookie('session')
        desk = self.get_cookie('desk')
        mydata.discussion[desk].add_customer(session)
        self.render('customer-order.html')

    @customer_auth
    def post(self):
        desk = self.get_cookie('desk')
        myorder = mydata.get_discussion_order(desk)
        response = {'status': 'ok', 'myorder': myorder}
        self.finish(json_encode(response))


class CustomerHistoryHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('customer-history.html')

    def post(self):
        uid = self.get_secure_cookie('session')
        #history = mydata.get_customer_history(uid)
        #response = {'status': 'ok', 'history': history}
        #self.finish(json_encode(response))







