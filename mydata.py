#coding=utf-8

import threading
import time
import uuid
import mydatabase
from tornado.concurrent import Future



mylock = threading.Lock()


#6w
#one_uid desk_uid diet_id stamp

#session desk_uid stamp

#uid stamp customers orders
#remember the last one in the same desk
last_desk_history = {}


class CustomerHistory(object):
    def __init__(self, uid, desk, submit, customer):
        self.uid = uid
        self.desk = desk
        self.submit = submit
        self.customer = customer


class DeskHistory(object):
    def __init__(self, uid, desk, submit, customer, order):
        self.desk = desk
        self.uid = uid
        self.submit = submit
        self.customer = customer
        self.order = order

    def store(self):
        pass
#diet category
#retrieve data from database


categories = mydatabase.get_category()
diet = mydatabase.get_diet()

#example
#
# uid is string not number
#desk is string

#for customer order disscussion
# {'1': {'desk': 1, 'gdemand': '', 'details': [,{  } ], 'sentby':' '} }
#                                   {'id':1, 'num':1, 'order': 1, 'price': 26,'demand': ' ', }
'''
 instruction format:
    {'+': {'did': , 'num': , 'demand': ,}}
    {'-': uuid}
    {'m':}
    {'submit': {'status':'none or confirmed ...', 'stamp': timestamp}}
    ready when client and server are synchronized    confirmed happens when confirm button is tapped when ready

'''
clipboard = {}


def init_role(fid):
    global cooks

    faculty = mydatabase.get_faculty()
    rows = filter(lambda x: x['id'] == fid, faculty)
    if not rows:
        return
    row = rows[0]
    if row['role'] == 'cook':
        if fid not in cooks:
            cooks[fid] = Cook(fid, row['name'])
    if row['role'] == 'waiter':
        if fid not in clipboard:
            pass


discussion = {}
# discussion ->  -> cook
#the final order

discussion_waiters = {}


#final_cache = []

# customer and waiter order
class OneOrder(object):

    def __init__(self, **kwargs):
        self.id = kwargs['id'] if 'id' in kwargs else None
        self.demand = kwargs['demand'] if 'demand' in kwargs else ''
        self.uid = str(uuid.uuid4())

        self.name = ''
        self.order = None
        self.price = None
        self.base = None
        self.cid = None

        self.status = 'none'
        #seek for infomation about id

        self.get_info()
        self.num = self.base
        self.desk = None

    def get_info(self):
        tmp = filter(lambda x: x['id'] == self.id, diet)
        if len(tmp) == 1:
            t = tmp[0]
            self.name = t['name']
            self.order = t['ord']
            self.price = t['price']
            self.base = t['base']
            self.cid = t['cid']
        return

    def from_one_order(self, one_order):
        self.id = one_order.id
        self.uid = str(uuid.uuid4())
        self.demand = one_order.demand

        self.cid = one_order.cid

        self.name = one_order.name
        self.order = one_order.order
        self.price = one_order.price
        self.base = one_order.base

        self.status = one_order.status
        #seek for infomation about id

        self.num = one_order.num
        self.desk = one_order.desk

    def from_dict(self, dictionary):
        self.id = dictionary['id'] if 'id' in dictionary else None
        self.num = dictionary['num'] if 'num' in dictionary else None
        self.demand = dictionary['demand'] if 'demand' in dictionary else None
        self.name = dictionary['name'] if 'demand' in dictionary else None
        self.order = dictionary['order'] if 'demand' in dictionary else None
        self.price = dictionary['price'] if 'demand' in dictionary else None
        self.base = dictionary['base'] if 'demand' in dictionary else None
        self.uid = dictionary['uid'] if 'uid' in dictionary else None
        self.cid = dictionary['cid'] if 'cid' in dictionary else None
        self.status = dictionary['status'] if 'status' in dictionary else 'none'
        self.desk = dictionary['desk'] if 'desk' in dictionary else None

    def to_dict(self):
        result = {'id': self.id, 'uid': self.uid, 'cid': self.cid, 'name': self.name, 'num': self.num, 'base': self.base,
                  'price': self.price, 'order': self.order, 'demand': self.demand,  'status': self.status, 'desk': self.desk}
        return result

    def equals(self, another):
        if isinstance(another, OneOrder):
            if self.id == another.id and self.num == another.num and self.demand == another.demand:
                return True
        return False

    def canmerge(self, another):
        if isinstance(another, OneOrder):
            if self.id == another.id and self.demand == another.demand:
                return True
        return False


class DeskOrder(object):

    def __init__(self, desk):
        self.uid = str(uuid.uuid4())
        self.desk = desk.upper()

        self.gdemand = ''
        self.details = []
        self.left = []
        self.selected = []
        self.doing = []
        self.done = []
        self.cancel = []
        self.by = ''
        self.stamp = time.time()
        #last done time for select
        self.submit = -1
        self.last = 0
        self.power = 0
        # status : none ready submit lock confirmed doing done
        self.status = 'none'
        self.customer = set()
        self.visits = 0

    def reset(self):
        self.uid = str(uuid.uuid4())
        self.gdemand = ''
        self.details = []
        self.left = []
        self.selected = []
        self.doing = []
        self.done = []
        self.cancel = []
        self.by = ''
        self.stamp = time.time()
        #last done time for select
        self.submit = -1
        self.last = 0
        self.power = 0
        # status : none ready submit lock confirmed doing done
        self.status = 'none'
        self.customer = set()
        self.visits = 0

    def check_submit(self):
        #check if the same one as the previous customer, yes then set stamp to the previous stamp
        global last_desk_history
        if self.desk in last_desk_history:
            last_desk = last_desk_history[self.desk]
            if self.customer & last_desk.customer:
                self.submit = last_desk.submit

    @property
    def confirmed(self):
        return self.done + self.doing + self.selected + self.left

    def calc_power(self):
        cur = time.time()
        self.power = 0.15 * (cur - self.submit) + 0.85 * (cur - self.last)
        return self.power

    def perform(self, who, ins):
        global customer_submits
        print who, ins
        if who == 'customer':
            if self.status == 'lock':
                customer_submits.request(self.desk)
                return
            self.stamp = time.time()

            # add a base piece
            if '+' in ins:
                self.status = 'none'
                # add new diet and merge with the previous same one
                one = ins['+']
                # one = {'id':,  'demand': } 'demand' may not be {'uid':,}
                if 'id' in one:
                    one_order = OneOrder(**one)
                    one_order.desk = self.desk
                    self.details.append(one_order)
                elif 'uid' in one:
                    filtered = filter(lambda x: x.uid == one['uid'], self.details)
                    if len(filtered) == 1:
                        one_order = filtered[0]
                        new_order = OneOrder()
                        new_order.from_one_order(one_order)
                        self.details.append(new_order)

            #{'-':{'id': id}} {'-':{'uid': uid}}
            elif '-' in ins:
                self.status = 'none'
                #delete diet
                one = ins['-']
                if 'id' in one:
                    self.details = filter(lambda x: x.id != one['id'], self.details)
                elif 'uid' in one:
                    self.details = filter(lambda x: x.uid != one['uid'], self.details)

            elif 'gd' in ins:
                self.status = 'none'
                #modify 'gdemand'
                self.gdemand = ins['gd']

            elif 'submit' in ins:
                if len(self.details) > 0:
                    if self.status == 'none':
                        self.status = 'ready'
                    elif self.status == 'ready':
                        self.status = 'submit'
                    if self.status == 'submit':
                        self.status = 'lock'
                        if self.submit == -1:
                            self.submit = time.time()
                        customer_submits.request(self.desk)

        elif who == 'waiter':
            self.stamp = time.time()

            # add a base piece
            if '+' in ins:
                self.status = 'none'
                # add new diet and merge with the previous same one
                one = ins['+']
                # one = {'id':,  'demand': } 'demand' may not be {'uid':,}
                if 'id' in one:
                    one_order = OneOrder(**one)
                    one_order.desk = self.desk
                    self.details.append(one_order)
                elif 'uid' in one:
                    filtered = filter(lambda x: x.uid == one['uid'], self.details + self.confirmed)
                    if len(filtered) > 0:
                        one_order = filtered[0]
                        new_order = OneOrder()
                        new_order.from_one_order(one_order)
                        self.details.append(new_order)

            #{'-':{'id': id}} {'-':{'uid': uid}}
            elif '-' in ins:
                self.status = 'none'
                #delete diet
                one = ins['-']
                if 'id' in one:
                    self.details = filter(lambda x: x.id != one['id'], self.details)
                elif 'uid' in one:
                    self.details = filter(lambda x: x.uid != one['uid'], self.details)
                    if one['uid'] in map(lambda x: x.uid, self.left) and one['uid'] not in map(lambda x: x.uid, globalByways):
                        self.left = filter(lambda x: x.uid != one['uid'], self.left)

            elif 'gd' in ins:
                self.status = 'none'
                #modify 'gdemand'
                self.gdemand = ins['gd']

            elif 'submit' in ins:
                if len(self.details) > 0:
                    if self.status == 'none':
                        self.status = 'ready'
                    elif self.status == 'ready':
                        self.status = 'submit'
                    if self.status == 'submit':
                        self.status = 'lock'
                        self.confirm()

        self.set_future()

    def confirm(self):
        self.stamp = time.time()
        if self.submit == -1:
            self.submit = time.time()
        self.store()
        self.left += self.details
        self.left.sort(key=lambda x: x.order)
        self.details = []
        self.status = 'confirmed'

    def cancel_submit(self):
        self.status = 'none'

    def add_customer(self, session):
        if session not in self.customer:
            self.customer.add(session)
            self.visits += self.get_visits(session)
            self.check_submit()

    def get_visits(self, session):
        return mydatabase.get_customer_visits(session)

    def insort(self):
        self.details.sort(key=lambda x: x.order)

    def select(self, index=0):
        if len(self.left) > index:
            one = self.left[index]
            self.selected.append(one)
            self.left.remove(one)
            self.last = time.time()
            return one
        return None

    def set_cancel(self, finalorder):
        pass

    def set_doing(self, finalorder):
        if finalorder in self.selected:
            self.selected.remove(finalorder)
            self.doing.insert(0, finalorder)
            #moved to select
            return True
        elif finalorder in self.left:
            self.left.remove(finalorder)
            self.doing.insert(0, finalorder)

            return True

        return False

    def set_finish(self, finalorder):
        if finalorder in self.doing:
            self.doing.remove(finalorder)
            self.done.append(finalorder)
            #moved to set_doing
            #self.last = time.time()
            self.vanish()
            return True
        return False

    def from_dict(self, dictionary):
        pass

    def to_dict(self):

        result = {'uid': self.uid, 'desk': self.desk, 'gdemand': self.gdemand, 'stamp': self.stamp, 'last': self.last,
                  'status': self.status,
                  'details': [x.to_dict() for x in self.details],
                  'left': [x.to_dict() for x in self.left],
                  'selected': [x.to_dict() for x in self.selected],
                  'doing': [x.to_dict() for x in self.doing],
                  'done': [x.to_dict() for x in self.done]}
        return result

    def set_future(self):
        global discussion_waiters
        if self.desk in discussion_waiters:
            futures = discussion_waiters[self.desk]

            for future in futures:
                try:
                    future.set_result(self.to_dict())
                finally:
                    pass
            discussion_waiters[self.desk] = set()

    def vanish(self):
        global discussion
        if len(self.details) + len(self.left) + len(self.selected) + len(self.doing) == 0:

            self.update_cache()
            del discussion[self.desk]

    def update_cache(self):
        global last_desk_history
        last_desk_history[self.desk] = self

    def store(self):
        #store details
        #customer history and order history
        #and cache

        for one in self.details:
            mydatabase.insert('order_history', {'one_uid': one.uid, 'id': one.id, 'desk_uid': self.uid, 'num': one.num, 'stamp': self.submit})
        for session in self.customer:
            mydatabase.insert('customer_history', {'session': session, 'desk': self.desk, 'desk_uid': self.uid, 'stamp': self.submit})


#functions
#for customer get myorder in discussion
def get_discussion_order(desk):
    global discussion
    desk = desk.upper()
    if desk not in mydatabase.desks:
        return None
    if desk not in discussion:
        return None
    return discussion[desk].to_dict()


#perform instructions to update myoreder in discussion
def discussion_perform(desk, who, instruction):
    global discussion
    desk = desk.upper()
    if desk not in mydatabase.desks:
        return None

    if desk not in discussion or discussion[desk] is None:
        discussion[desk] = DeskOrder(desk)

    discussion[desk].perform(who, instruction)

    return discussion[desk].to_dict()


#  for updaters and maybe wait

def discussion_order_update(desk, stamp):
    global discussion, discussion_waiters
    future = Future()
    desk = desk.upper()
    if desk not in mydatabase.desks:
        future.set_result(None)
#  if server crashes, discussion will lose data, desk_order is None , immediate response lead to polling
    if desk not in discussion or discussion[desk] is None:
        discussion[desk] = DeskOrder(desk)
        #future.set_result(None)

    if desk not in discussion_waiters or discussion_waiters[desk] is None:
        discussion_waiters[desk] = set()

    print 'discussion_update  desk: %s :' % desk, discussion[desk].to_dict()
    if stamp < discussion[desk].stamp:
        future.set_result(discussion[desk].to_dict())
    else:
        discussion_waiters[desk].add(future)
    return future


# select one order from final into final_cache
# select algorithm
FINAL_CACHE_SIZE = 3

def select_order():
    global discussion, globalByways

    deskorders = filter(lambda x: x is not None and len(x.left) > 0, discussion.values())
    if deskorders:
        for desk_order in deskorders:
            desk_order.get_power()
        deskorders.sort(key=lambda x: x.power)
        deskorders.reverse()
        for desk_order in deskorders:
            left = desk_order.left
            one = left[0]
            tmp = filter(lambda x: x.order <= one.order, left)
            for one_order in tmp:
                if one_order not in globalByways:
                    index = left.index(one_order)
                    desk_order.select(index)
                    return one_order
                else:
                    continue
    return None



# contain cook's current and byways for distinct selection
# mark occupied status by cook, including cook's current
globalByways = []

# each cook has
#select byway form left
BYWAY_SIZE = 6

def byway_order(finalorder):
    #find in final_cache first
    global globalByways, discussion
    tmp = []
    deskorders = filter(lambda x: x is not None and len(x.left) > 0, discussion.values())

    for desk_final in deskorders:
        left = desk_final.left
        for byway in left:
            #not proper time
            if byway.order < finalorder.order:
                break
            if byway.id == finalorder.id and byway_order not in globalByways:
                tmp.append(byway)
                if len(tmp) >= BYWAY_SIZE:
                    return tmp
    return tmp


# for cooks {'id': cook}
cooks = {}

def get_mycook(fid):
    global cooks

    if fid not in cooks or cooks[fid] is None:

        cooks[fid] = Cook(fid)
    return cooks[fid].to_dict()



# finalorder status  confirmed seleted/byway
# each instance matches one cook
class Cook(object):

    def __init__(self, fid, name=''):
        self.fid = fid
        self.name = name
        self.uid = None
        self.current = None
        self.byway = []
        self.doing = []
        self.done = []
        self.cancel = []
        #self.selected = []
        self.waiters = []
        #working rest
        self.status = 'working'
        self.stamp = 0

    # accept current takens and doing, remove current one and byways ,then take new one and byways
    def accept(self, takens):

        if self.current is None:

            self.take()
            return
        #takens include self.current and byway_selected
        if len(takens) == 0:

            self.take()
            return
        # may never happen
        if self.current.uid not in takens:
            self.clear()
            return

        #doing takens
        # handle doing , self.current  deskfinal  final_cache globalByways pointer
        for uid in takens:
            self.set_doing(uid)
        #reomve current one and byways from globalByways status
        #remove byway status not selected
        global globalByways
        if self.current is not None:
            self.byway.append(self.current)
        globalByways = filter(lambda x: x not in self.byway, globalByways)

        self.current = None
        self.byway = []


    #take one from desk_order as self.current
    def take(self):
        global globalByways

        if self.current is not None:
            return False
        if self.byway:
            return False
        #take current
        one = select_order()
        self.current = one

        if self.current is not None:
            globalByways.append(self.current)
            self.byway = byway_order(self.current)
            globalByways += self.byway

            return True
        self.byway = []
        return False

    def clear(self):
        global globalByways
        if self.current is not None:
            self.byway.append(self.current)
        globalByways = filter(lambda x: x not in self.byway, globalByways)
        self.current = None
        self.byway = []

    def set_doing(self, uid):
        global globalByways, discussion
        if uid == self.current.uid:
            self.current.status = 'doing'
            self.doing.insert(0, self.current)
            discussion[self.current.desk].set_doing(self.current)

            globalByways.remove(self.current)
            self.current = None
            return True

        elif uid in map(lambda x: x.uid, self.byway):
            desk_order = filter(lambda x: x.uid == uid, self.byway)[0]
            desk_order.status = 'doing'
            self.doing.insert(0, desk_order)
            self.byway.remove(desk_order)
            discussion[desk_order.desk].set_doing(desk_order)

            globalByways.remove(desk_order)

            return True
        return False

    def cancel_doing(self, uid):
        #insert into desk.left
        global discussion

        orders = filter(lambda x: x.uid == uid, self.doing)
        if orders:
            order = orders[0]
            self.doing.remove(order)
            self.cancel.append(order)
            order.status = 'canceled'
            desk_order = discussion[order.desk]
            desk_order.doing.remove(order)
            desk_order.cancel.append(order)

            return True
        return False

    def set_finish(self, uid):
        global discussion
        if uid in map(lambda x: x.uid, self.doing):
            order = filter(lambda x: x.uid == uid, self.doing)[0]
            self.doing.remove(order)
            self.done.append(order)
            if len(self.done) > 20:
                self.done = self.done[-20:]
            desk_order = discussion[order.desk]
            desk_order.set_finish(order)
            self.finish_request(order)

            #store in mysql
            mydatabase.insert('cook_history', {'fid': self.fid, 'uid': order.uid, 'id': order.id, 'stamp': time.time()})

            return True
        return False

    def finish_request(self, order):
        global cook_finish
        request = (order.uid, order.name, order.num, order.desk, self.fid, self.name)
        cook_finish.request(request)

    def refuse(self):
        # release occupied status in globalByways
        self.clear()
        self.take()
        return

    def perform(self, ins):
        if 'accept' in ins:
            takens = ins['accept']
            self.accept(takens)
        elif 'refuse' in ins:
            self.refuse()
        elif 'finish' in ins:
            self.set_finish(ins['finish'])
        elif 'cancel' in ins:
            self.cancel_doing(ins['cancel'])
        elif 'stop' in ins:
            self.clear()

    def call(self):
        pass

    def update(self):
        pass

    def to_dict(self):
        result = {'fid': self.fid, 'uid': self.uid, 'name': self.name,
                  'current': self.current.to_dict() if self.current is not None else None,
                  'byway': [x.to_dict() for x in self.byway],
                  'doing': [x.to_dict() for x in self.doing],
                  'done': [x.to_dict() for x in self.done],
                  'cancel': [x.to_dict() for x in self.cancel],
                  'status': self.status,
                  'stamp': self.stamp}
        return result


def cook_perform(fid, ins):
    global cooks
    if fid not in cooks:
        mycook = Cook(fid)
        cooks[fid] = mycook
    cooks[fid].perform(ins)
    return cooks[fid].to_dict()


class CustomerRequestBuffer(object):

    def __init__(self):
        self.waiters = set()
        #for requests
        self.buffer = []
        self.stamp = time.time()

    def request(self, desk):
        if desk is None:
            return
        if desk not in self.buffer:
            self.buffer.append(desk)
            self.buffer.sort()
            self.stamp = time.time()
        self.set_future()
        return self.buffer

    def answer(self, desk):
        if desk in self.buffer:
            self.buffer.remove(desk)
            self.stamp = time.time()
        self.set_future()
        return self.buffer

    def set_future(self):
        for future in self.waiters:
            try:
                future.set_result(self.buffer)
            finally:
                pass
        self.waiters = set()

    def update(self, stamp):
        future = Future()
        if stamp < self.stamp:
            future.set_result(self.buffer)
        else:
            self.waiters.add(future)
        return future


class CookRequestBuffer(object):
    def __init__(self):
        self.waiters = set()
        #for requests
        #(fid, name)
        self.buffer = []
        self.stamp = time.time()

    def request(self, fid):
        if fid is None:
            return

        fids = map(lambda x: x[0], self.buffer)
        global cooks
        #cursor.execute('select * from faculty where id=:fid', {'fid': fid})
        #row = cursor.fetchone()
        #name = row['name']
        name = cooks[fid].name
        if fid not in fids:
            self.buffer.append((fid, name))

            self.stamp = time.time()
        self.set_future()
        return self.buffer

    def answer(self, fid):

        self.buffer = filter(lambda x: x[0] != fid, self.buffer)
        self.stamp = time.time()
        self.set_future()
        return self.buffer

    def set_future(self):
        for future in self.waiters:
            try:
                future.set_result(self.buffer)
            finally:
                pass
        self.waiters = set()

    def update(self, stamp):
        future = Future()
        if stamp < self.stamp:
            future.set_result(self.buffer)
        else:
            self.waiters.add(future)
        return future


class CookFinishBuffer(object):

    def __init__(self):
        self.waiters = set()
        #for requests
        self.buffer = []
        self.stamp = time.time()

    def request(self, finish):
        if finish is None:
            return
        #(uid, name, num, desk, fid, cookname)
        if finish not in self.buffer:
            self.buffer.append(finish)

            self.stamp = time.time()
        self.set_future()
        return self.buffer

    def answer(self, uid):
        self.buffer = filter(lambda x: x[0] != uid, self.buffer)
        self.stamp = time.time()
        self.set_future()
        return self.buffer

    def set_future(self):
        for future in self.waiters:
            try:
                future.set_result(self.buffer)
            finally:
                pass
        self.waiters = set()

    def update(self, stamp):
        future = Future()
        if stamp < self.stamp:
            future.set_result(self.buffer)
        else:
            self.waiters.add(future)
        return future
customer_requests = CustomerRequestBuffer()
customer_submits = CustomerRequestBuffer()
cook_requests = CookRequestBuffer()
cook_finish = CookFinishBuffer()




