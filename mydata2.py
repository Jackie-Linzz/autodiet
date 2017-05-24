#coding=utf-8

import threading
import time
import uuid

from tornado.concurrent import Future

from mydatabase import conn

mylock = threading.Lock()

cursor = conn.cursor()


#diet category
#retrieve data from database
diet_category_one = {'id': 1, 'name': '主食', 'order': 3, 'desc': '', 'picture': ''}
categories = []
categories_sorted = []


def update_categories():
    global cursor, categories, categories_sorted
    categories = []
    cursor.execute('select * from category')
    for row in cursor.fetchall():
        categories.append({'id': row['id'], 'name': row['name'], 'order': row['ord'],
                           'desc': row['desc'], 'picture': row['picture']})
    categories.sort(key=lambda x: x['order'])
    categories_sorted = categories

update_categories()


#example
#
#id uid is string not number
#desk is string
diet_all = []
diet_all_sorted = []


def update_diet():
    global diet_all, cursor, diet_all_sorted
    diet_all = []
    cursor.execute('select * from diet')
    for row in cursor.fetchall():
        diet_all.append({'id': row['id'], 'name': row['name'], 'price': row['price'], 'cid': row['cid'],
                         'order': row['ord'], 'picture': row['picture'], 'base': row['base'], 'desc': row['desc']})
    diet_all.sort(key=lambda x: x['order'])
    diet_all_sorted = diet_all

#diet_one = {'id': 1, 'name': '', 'cid': 1, 'order': 1, 'picture': '', 'base': 1, 'desc': '', }

update_diet()




#order example
order_detail = {'id': 4, 'num': 1, 'demand': ''}
order_one = {'id': 1, 'desk': 418, 'gdemand': '', 'detail': []}

#for customer order disscussion
# {'1': {'desk': 1, 'gdemand': '', 'details': [,{  } ], 'sentby':' '} }
#                                   {'id':1, 'num':1, 'order': 1, 'price': 26,'demand': ' ', }
'''
 instruction format:
    {'+': {'id': , 'num': , 'demand': ,}}
    {'-': uuid}
    {'m':}
    {'go': {'status':'none or confirmed ...', 'stamp': timestamp}}
    ready when client and server are synchronized    confirmed happens when confirm button is tapped when ready

'''

discussion = {0: {'desk': 1, 'gdemand': '',
                  'details': [{'id': 1, 'num': 1, 'order': 1, 'price': 26, 'base': 1, 'demand': '', }],
                  'by': ''}}
# discussion -> final -> select -> final_cache -> cook
#the final order

discussion_waiters = {}

final = {}

final_waiters = {}

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
        tmp = filter(lambda x: x['id'] == self.id, diet_all_sorted)
        if len(tmp) == 1:
            t = tmp[0]
            self.name = t['name']
            self.order = t['order']
            self.price = t['price']
            self.base = t['base']
            self.cid = t['cid']
        return

    def from_one_order(self, one_order):
        self.id = one_order.id
        self.demand = one_order.demand
        self.uid = str(uuid.uuid4())
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
        self.desk = desk
        self.gdemand = ''
        self.confirmed = []
        self.details = []
        self.by = ''
        self.stamp = time.time()
        # status : none ready submit | confirmed doing done
        self.status = 'none'

        self.uid = str(uuid.uuid4())
        self.customer = []

    @property
    def done(self):
        if len(self.details) > 0:
            return False
        else:
            return True

    def perform(self, ins):
        if self.status == 'lock':
            return
        self.stamp = time.time()
        print ins
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
            gdemand = ins['gd']
            if self.gdemand != gdemand:

                self.gdemand = gdemand

        elif 'submit' in ins:
            if len(self.details) > 0:
                if self.status == 'none':
                    self.status = 'ready'
                elif self.status == 'ready':
                    self.status = 'submit'
                if self.status == 'submit':
                    self.status = 'lock'
                    global customer_submits
                    customer_submits.request(self.desk)
                    self.store()

        self.set_future()

    def insort(self):
        self.details.sort(key=lambda x: x.order)

    def from_dict(self, dictionary):
        pass

    def to_dict(self):
        details = map(lambda x: x.to_dict(), self.details)
        confirmed = map(lambda x: x.to_dict(), self.confirmed)
        result = {'desk': self.desk, 'gdemand': self.gdemand, 'details': details, 'confirmed': confirmed,
                  'by': self.by, 'stamp': self.stamp, 'status': self.status, 'uid': self.uid}
        return result

    def set_future(self):
        global discussion_waiters
        if self.desk in discussion_waiters:
            futures = discussion_waiters[self.desk]

            for future in futures:
                future.set_result(self.to_dict())
            discussion_waiters[self.desk] = set()

    def store(self):
        global cursor
        sql = 'insert into customer_history (session_id,one_uid,name,num,guid,stamp) values (:sid,:one_uid,:name,:num,:guid,:stamp)'
        data = [{'sid': customer, 'one_uid': x.uid, 'name': x.name, 'num': x.num, 'guid': self.uid, 'stamp': self.stamp}
                for customer in self.customer for x in self.details]
        cursor.executemany(sql, data)
        conn.commit()

#  for updaters and maybe wait

def discussion_order_update(desk, stamp):
    global discussion, discussion_waiters
    future = Future()
#  if server crashes, discussion will lose data, desk_order is None , immediate response lead to polling
    if desk not in discussion:
        discussion[desk] = DeskOrder(desk)
        #future.set_result(None)

    if desk not in discussion_waiters:
        discussion_waiters[desk] = set()

    print 'discussion  desk: %s :' % desk, discussion[desk].to_dict()
    if stamp < discussion[desk].stamp:
        future.set_result(discussion[desk].to_dict())
    else:
        discussion_waiters[desk].add(future)
    return future


# waiter can cancel left order
class DeskFinal(object):
    def __init__(self):
        self.status = 'confirmed'
        self.uid = None
        self.left = []
        self.selected = []
        self.doing = []
        self.done = []
        self.stamp = 0
        self.gdemand = ''
        self.desk = ''
        #last done time for select
        self.last = 0
        self.power = 0


    # called only once
    def from_desk_order(self, desk_order):
        self.stamp = desk_order.stamp
        self.uid = desk_order.uid
        self.gdemand = desk_order.gdemand
        self.desk = desk_order.desk
        self.left = [] + desk_order.details
        #adjust demand = demand + gdemand
        for one_order in self.left:
            one_order.demand = (one_order.demand + ',' + self.gdemand).strip()
            one_order.desk = self.desk
            one_order.status = 'confirmed'
        self.left.sort(key=lambda x: x.id)
        self.left.sort(key=lambda x: x.order)

    def get_power(self):
        cur = time.time()
        self.power = 0.15 * (cur - self.stamp) + 0.85 * (cur - self.last)
        return self.power

    def select(self, index=0):
        if len(self.left) > index:
            one = self.left[index]
            self.selected.append(one)
            self.left.remove(one)
            self.last = time.time()
            return one
        return None

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

    def add(self, one_orders):
        for one_order in one_orders:
            one_order.demand = (one_order.demand + ',' + self.gdemand).strip()
            one_order.desk = self.desk
            one_order.status = 'confirmed'
        self.left += one_orders

    def store(self):
        #sotre in order_history
        global cursor
        data = [{'one_uid': x.uid, 'guid': self.uid, 'name': x.name, 'num': x.num, 'stamp': self.stamp} for x in self.done]
        sql = 'insert into order_history (one_uid, guid, name, num, stamp) values (:one_uid,:guid,:name,:num,:stamp)'
        cursor.executemany(sql, data)
        conn.commit()

    def vanish(self):
        global discussion
        if len(self.left) + len(self.selected) + len(self.doing) == 0:
            desk_order = discussion[self.desk]
            if desk_order.status not in ('submit', 'lock'):
                self.store()
                discussion[self.desk] = None
                final[self.desk] = None

#after customer submits , waiter confirm order, push it into final
def confirm_desk_order(desk):
    global discussion, final
    deskorder = discussion[desk]
    if final[desk] is None:
        deskfinal = DeskFinal()
        deskfinal.from_desk_order(deskorder)
    else:
        deskfinal.add(deskorder.details)
    deskorder.confirmed += deskorder.details
    deskorder.details = []
    deskorder.status = 'confirmed'
    deskorder.stamp = time.time()
    deskorder.set_future()


# select one order from final into final_cache
# select algorithm
FINAL_CACHE_SIZE = 3



def select_order():
    global discussion, final, FINAL_CACHE_SIZE

    deskfinals = filter(lambda x: x is not None and len(x.left) > 0, final.values())
    if deskfinals:
        for desk_final in deskfinals:
            desk_final.get_power()
        deskfinals.sort(key=lambda x: x.power)
        deskfinals.reverse()
        for desk_final in deskfinals:
            left = desk_final.left
            one = left[0]
            tmp = filter(lambda x: x.order <= one.order, left)
            for one_order in tmp:
                if one_order not in globalByways:
                    index = left.index(one_order)
                    desk_final.select(index)
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
    global globalByways
    tmp = []
    deskfinals = filter(lambda x: x is not None and len(x.left) > 0, final.values())

    for desk_final in deskfinals:
        left = desk_final.left
        for byway_order in left:
            #not proper time
            if byway_order.order < finalorder.order:
                break
            if byway_order.id == finalorder.id and byway_order not in globalByways:
                tmp.append(byway_order)
                if len(tmp) >= BYWAY_SIZE:
                    return tmp
    return tmp


# for cooks {'id': cook}
cooks = {}

def get_mycook(fid):
    global cooks
    mycook = None
    if fid not in cooks:
        mycook = Cook(fid)
        cooks[fid] = mycook
    return mycook.to_dict()



# finalorder status  confirmed seleted/byway
# each instance matches one cook
class Cook(object):

    def __init__(self, fid):
        self.fid = fid
        self.uid = None
        self.current = None
        self.byway = []
        self.doing = []
        self.done = []
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
        self.byway.append(self.current)
        globalByways = filter(lambda x: x not in self.byway, globalByways)

        self.current = None
        self.byway = []
        self.take()

    #take one from final_cache as self.current
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
            self.byway = byway_order(self.current)
            globalByways += self.byway
            globalByways.append(self.current)
            return True
        return False

    def clear(self):
        global globalByways
        if self.current is not None:
            self.byway.append(self.current)
            globalByways = filter(lambda x: x not in self.byway, globalByways)
            self.current = None
            self.byway = []

    def set_doing(self, uid):
        global globalByways, final
        if uid == self.current.uid:
            self.current.status = 'doing'
            self.doing.insert(0, self.current)
            final[self.current.desk].set_doing(self.current)

            globalByways.remove(self.current)
            self.current = None
            return True

        elif uid in map(lambda x: x.uid, self.byway):
            finalorder = filter(lambda x: x.uid == uid, self.byway)[0]
            finalorder.status = 'doing'
            self.doing.insert(0, finalorder)
            self.byway.remove(finalorder)
            final[finalorder.desk].set_doing(finalorder)

            globalByways.remove(finalorder)

            return True
        return False

    def cancel_doing(self, uid):
        #insert into deskfinal.left
        global final
        if uid in map(lambda x: x.uid, self.doing):
            finalorder = filter(lambda x: x.uid == uid, self.doing)[0]
            self.doing.remove(finalorder)
            finalorder.status = 'confirmed'
            deskfinal = final[finalorder.desk]
            deskfinal.doing.remove(finalorder)
            deskfinal.left.insert(0, finalorder)

            return True
        return False

    def set_finish(self, uid):
        if uid in map(lambda x: x.uid, self.doing):
            finalorder = filter(lambda x: x.uid == uid, self.doing)[0]
            self.doing.remove(finalorder)
            self.done.append(finalorder)
            if len(self.done) > 20:
                self.done = self.done[-20:]
            deskfinal = final[finalorder.desk]
            deskfinal.set_finish(finalorder)

            return True
        return False

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
        result = {'fid': self.fid, 'uid': self.uid, 'current': self.current.to_dict(),
                  'byway': [x.to_dict() for x in self.byway],
                  'doing': [x.to_dict() for x in self.doing],
                  'done': [x.to_dict() for x in self.done],
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

#functions
#for customer get myorder in discussion
def get_discussion_order(desk):
    global discussion
    if desk not in discussion:
        return None
    return discussion[desk].to_dict()


#perform instructions to update myoreder in discussion
def discussion_perform(desk, instruction):
    global discussion

    if desk not in discussion:
        discussion[desk] = DeskOrder(desk)

    discussion[desk].perform(instruction)

    return discussion[desk].to_dict()


def waiter_del(desk, ins):
    global discussion, final, globalByways
    if '-' not in ins:
        return
    if 'uid' not in ins['-']:
        return
    uid = ins['-']['uid']
    desk_order = discussion[desk]
    if uid in map(lambda x: x.uid, desk_order.details):
        desk_order.perform(ins)
        return desk_order.to_dict()
    if desk not in final:
        return
    desk_final = final[desk]
    if uid in map(lambda x: x.uid, desk_final.left):

        one = filter(lambda x: x.uid == uid, desk_final.left)[0]
        if one not in globalByways:
            desk_final.left.remove(one)
            desk_order.confirmed.remove(one)
            desk_order.stamp = time.time()
            desk_order.set_future()
            return desk_order.to_dict()

def waiter_submit(desk, ins):
    global discussion, final
    discussion_perform(desk, ins)
    confirm_desk_order(desk)
    return discussion[desk].to_dict()

class CustomerRequestBuffer(object):

    def __init__(self):
        self.waiters = set()
        #for requests
        self.buffer = []
        self.stamp = time.time()

    def request(self, desk):
        if desk not in self.buffer:
            self.buffer.append(desk)
            self.buffer.sort()
            self.stamp = time.time()
        for future in self.waiters:
            future.set_result(self.buffer)


    def answer(self, desk):
        if desk in self.buffer:
            self.buffer.remove(desk)
            self.stamp = time.time()
        for future in self.waiters:
            future.set_result(self.buffer)
        self.waiters = set()
        return self.buffer

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
        fids = map(lambda x: x[0], self.buffer)
        global cursor
        cursor.execute('select * from faculty where id=:fid', {'fid': fid})
        row = cursor.fetchone()
        name = row['name']
        if fid not in fids:
            self.buffer.append((fid, name))

            self.stamp = time.time()
        for future in self.waiters:
            future.set_result(self.buffer)

    def answer(self, fid):

        self.buffer = filter(lambda x: x[0] != fid, self.buffer)
        self.stamp = time.time()
        for future in self.waiters:
            future.set_result(self.buffer)
        self.waiters = set()
        return self.buffer

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

def customer_history(uid, num=5):
    global cursor

