import tornado.web
import tornado.gen
import functools

from tornado.escape import json_encode, json_decode

import mydata
import mydatabase


def waiter_auth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        who = self.get_secure_cookie('who', None)
        fid = self.get_secure_cookie('fid', None)
        desk = self.get_cookie('desk', None)
        #desk should in reasonable range, here is a simple check
        if who != 'waiter' or fid is None or desk is None:
            response = {'status': 'denied', 'next': '/'}
            self.finish(json_encode(response))
            return

        return method(self, *args, **kwargs)
    return wrapper

# waiter request page
class WaiterRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_cookie('_xsrf', self.xsrf_token)

        self.render('waiter-request.html')

# answer request
    def post(self):
        fid = self.get_argument('cook_request', None)
        request_desk = self.get_argument('customer_request', None)
        submit_desk = self.get_argument('customer_submit', None)
        gbuffer = None
        if fid:
            fid = json_decode(fid)
            gbuffer = mydata.cook_requests.answer(fid)
        if request_desk:
            request_desk = json_decode(request_desk)
            gbuffer = mydata.customer_requests.answer(request_desk)
        if submit_desk:
            submit_desk = json_decode(submit_desk)
            gbuffer = mydata.customer_submits.answer(submit_desk)
            mydata.discussion[submit_desk].confirm()
            mydata.discussion[submit_desk].set_future()

        response = {'status': 'ok', 'buffer': gbuffer}
        self.write(json_encode(response))


class WaiterCustomerRequestUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        stamp = json_decode(self.get_argument('stamp'))
        gbuffer = yield mydata.customer_requests.update(stamp)
        response = {'status': 'ok', 'stamp': mydata.customer_requests.stamp, 'buffer': gbuffer}
        self.write(json_encode(response))
        raise tornado.gen.Return()


class WaiterCustomerSubmitUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        stamp = json_decode(self.get_argument('stamp'))
        gbuffer = yield mydata.customer_submits.update(stamp)
        response = {'status': 'ok', 'stamp': mydata.customer_submits.stamp, 'buffer': gbuffer}
        self.write(json_encode(response))
        raise tornado.gen.Return()


class WaiterCookRequestUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        stamp = json_decode(self.get_argument('stamp'))
        gbuffer = yield mydata.cook_requests.update(stamp)
        response = {'status': 'ok', 'stamp': mydata.cook_requests.stamp, 'buffer': gbuffer}
        self.write(json_encode(response))
        raise tornado.gen.Return()


#waiter category page

class WaiterCategoryHandler(tornado.web.RequestHandler):

    def get(self):
        self.clear_cookie('cid')
        self.render('waiter-category.html')

    def post(self):
        diet = mydata.diet
        categories = mydata.categories
        response = {'status': 'ok', 'diet': diet, 'categories': categories}
        self.write(json_encode(response))


#desk is not secure cookie
class WaiterCategoryLoginHandler(tornado.web.RequestHandler):
    def post(self):
        desk = json_decode(self.get_argument('desk'))
        desk = desk.upper()
        if mydatabase.check_desk(desk):
            self.set_cookie('desk', desk)

            myorder = mydata.get_discussion_order(desk)
            response = {'status': 'ok',  'myorder': myorder, 'desk': desk}
        else:
            response = {'status': 'no desk'}
        self.write(json_encode(response))


class WaiterCategoryLogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie('desk')
        response = {'status': 'ok'}
        self.write(json_encode(response))


class WaiterCategoryToDetailHandler(tornado.web.RequestHandler):
    def post(self):
        cid = json_decode(self.get_argument('cid'))
        self.set_cookie('cid', str(cid))
        response = {'status': 'ok', 'next': '/waiter-detail?hh=0'}
        self.write(json_encode(response))





#waiter detail page
class WaiterDetailHandler(tornado.web.RequestHandler):
    @waiter_auth
    def get(self):
        self.render('waiter-detail.html')

    @waiter_auth
    def post(self):
        cid = int(self.get_cookie('cid'))
        desk = self.get_cookie('desk')
        response = {'status': 'ok', 'cid': cid, 'diet': mydata.diet, 'desk': desk,
                    'myorder': mydata.get_discussion_order(desk), 'categories': mydata.categories}
        self.write(json_encode(response))



class WaiterDetailOrderHandler(tornado.web.RequestHandler):
    #handle deskorder
    @waiter_auth
    def post(self):
        who = self.get_secure_cookie('who')
        desk = self.get_cookie('desk')
        ins = json_decode(self.get_argument('instruction'))
        myorder = mydata.discussion_perform(desk, who, ins)
        response = {'status': 'ok', 'myorder': myorder}
        self.write(json_encode(response))






class WaiterOrderHandler(tornado.web.RequestHandler):
    @waiter_auth
    def get(self):
        self.render('waiter-order.html')

    @waiter_auth
    def post(self):
        desk = self.get_cookie('desk')
        myorder = mydata.get_discussion_order(desk)
        response = {'status': 'ok', 'desk': desk, 'myorder': myorder}
        self.finish(json_encode(response))


class WaiterOrderOrderHandler(tornado.web.RequestHandler):
    @waiter_auth
    def post(self):
        desk = self.get_cookie('desk', '')
        if desk == '':
            self.finish()
            return
        who = self.get_secure_cookie('who')
        ins = json_decode(self.get_argument('instruction'))
        myorder = mydata.discussion_perform(desk, who, ins)
        response = {'status': 'ok', 'myorder': myorder}
        self.write(json_encode(response))


class WaiterOrderUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        desk = self.get_cookie('desk')
        stamp = json_decode(self.get_argument('stamp'))
        myorder = yield mydata.discussion_order_update(desk, stamp)
        response = {'status': 'ok', 'myorder': myorder}
        self.write(json_encode(response))
        raise tornado.gen.Return()


# waiter search page
class WaiterSearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('waiter-search.html')

    def post(self):
        desk = self.get_cookie('desk')
        diet = mydata.diet
        myorder = mydata.get_discussion_order(desk)
        response = {'status': 'ok', 'diet': diet, 'myorder': myorder}
        self.write(json_encode(response))


class WaiterTransferHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('waiter-transfer.html')

    def post(self):
        pass


class WaiterTransferAnswerHandler(tornado.web.RequestHandler):

    def post(self):
        uid = json_decode(self.get_argument('uid'))
        transfer = mydata.cook_finish.answer(uid)
        response = {'status': 'ok', 'transfer': transfer}
        self.finish(json_encode(response))


class WaiterTransferUpdateHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        stamp = json_decode(self.get_argument('stamp'))
        gbuffer = yield mydata.cook_finish.update(stamp)
        response = {'status': 'ok', 'stamp': mydata.cook_finish.stamp, 'transfer': gbuffer}
        self.finish(json_encode(response))
        raise tornado.gen.Return()

