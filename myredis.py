import redis
import mysql
import logging
import util
from tornado.escape import json_encode, json_decode

r = redis.StrictRedis()

r.setnx('order_history_th', 1)
r.setnx('customer_history_th', 1)
r.setnx('cook_history_th', 1)
r.setnx('comment_th', 1)
r.setnx('diet_stat_th', 1)
r.setnx('cook_stat_th', 1)
#mysql for diet category faculty
#redis for comment
#redis and mysql for history and stat
#sync_cache = {'table': '', 'act': '+/-', 'row': row}

#cache_table = ['order_history', 'customer_history', 'cook_history', 'diet_stat', 'cook_stat']


# rows is list of dict
def insert_many(table, rows):
    if table not in ('comment', 'order_history', 'customer_history', 'cook_history', 'diet_stat', 'cook_stat'):
        return False
    try:

        p = r.pipeline()
        for row in rows:

            th = r.get('%s_th' % table)
            row['th'] = int(th)
            p.lpush('%s' % table, th)
            p.hmset('%s:%s' % (table, th), row)

            p.incr('%s_th' % table)
            mysql.insert(table, row)
            p.execute()

            #insert into mysql
        return True
    except Exception, e:
        logging.error(e)
        return False


def insert(table, row):
    return insert_many(table, [row])


def delete(table, row):
    if table not in ('comment', 'order_history', 'customer_history', 'cook_history', 'diet_stat', 'cook_stat'):
        return False
    try:
        th = row['th']
        r.lrem(table, 0, th)
        r.delete('%s:%s' % (table, th))
        mysql.delete(table, row)
        return True
    except Exception, e:
        logging.error(e)
        return False


#get all keys low efficiency
def indextostamp(table, index):
    th = r.lindex(table, index)
    stamp = r.hget('%s:%s' % (table, th), 'stamp')
    return float(stamp)


def index_range(table, time_from, time_to):
    if time_from >= time_to:
        return None, None
    length = r.llen(table)
    if not length:
        return None, None
    if time_from > indextostamp(table, 0):
        return None, None
    if time_to < indextostamp(table, -1):
        return None, None



    i_start = 0
    i_end = -1

    start = 0
    end = length - 1
    while True:
        mid = int((start + end) / 2)

        if (end - start) <= 18:
            i_end = end
            keys = r.lrange('%s' % table, start, end)
            p = r.pipeline()
            for key in keys:
                p.hgetall('%s:%s' % (table, key))
            rows = p.execute()

            for row in rows:
                if float(row['stamp']) < time_from:
                    i = rows.index(row)
                    if start + i - 1 >= 0:
                        i_end = start + i - 1
                    else:
                        i_end = start + i
                    break
            break

        if time_from < indextostamp(table, mid):
            start = mid
        elif time_from > indextostamp(table, mid):
            end = mid
        else:
            i_end = mid
            break

    start = 0
    end = length - 1
    while True:
        mid = int((start + end) / 2)
        if end - start <= 18:
            i_start = start
            keys = r.lrange('%s' % table, start, end)
            p = r.pipeline()
            for key in keys:
                p.hgetall('%s:%s' % (table, key))
            rows = p.execute()
            for row in rows:
                i = rows.index(row)
                i_start = start + i
                if float(row['stamp']) < time_to:
                    break
            break

        if time_to < indextostamp(table, mid):
            start = mid
        elif time_to > indextostamp(table, mid):
            end = mid
        else:
            if mid + 1 <= length - 1:
                i_start = mid + 1
            else:
                i_start = mid
            break
    return i_start, i_end


def get(table, time_from, time_to):
    if table not in ('comment', 'order_history', 'customer_history', 'cook_history', 'diet_stat', 'cook_stat'):
        return []
    start, end = index_range(table, time_from, time_to)
    if start is None:
        return []
    keys = r.lrange(table, start, end)
    p = r.pipeline()
    for key in keys:
        p.hgetall('%s:%s' % (table, key))
    res = p.execute()
    return res


def get_all(table):
    if table not in ('comment', 'order_history', 'customer_history', 'cook_history', 'diet_stat', 'cook_stat'):
        return []
    keys = r.lrange(table, 0, -1)
    p = r.pipeline()
    for key in keys:
        p.hgetall('%s:%s' % (table, key))
    res = p.execute()
    return res


def get_comment(start, count):
    try:
        temp = []
        keys = r.lrange('comment', start, start + count - 1)

        p = r.pipeline()
        for key in keys:
            p.hgetall('comment:%s' % key)
        rows = p.execute()
        temp = filter(lambda x: bool(x), rows)

        return temp
    except Exception, e:
        print e
        return []




def get_customer_visits(session, count=50000):
    num = 0
    keys = r.lrange('customer_history', 0, count)

    p = r.pipeline()
    for key in keys:
        p.hgetall('%s:%s' % ('customer_history', key))
    rows = p.execute()
    for row in rows:
        if row['session'] == session:
            num += 1
    return num



'''
def insert_order_history(one_uid='', desk_uid='', id=-1, num=0, stamp=0):
    if not(one_uid and desk_uid and num):
        return False

    try:
        key = r.get('order_history_key')

        p = r.pipeline()
        p.lpush('order_history', key)
        p.hmset('order_history:%s' % key, {'one_uid': one_uid, 'desk_uid': desk_uid, 'id': id, 'num': num, 'stamp': stamp})
        p.incr('order_history_key')
        p.execute()
        return True
    except Exception, e:
        print e
        return False


def get_order_history(time_from, time_to):
    try:
        if time_from > time_to:
            return []
        temp = []
        keys = r.lrange('order_history', 0, -1)

        point = None
        for key in keys:
            one = r.hgetall('order_history:%s' % key)
            if one == {}:
                point = int(key)
                break
            if time_from <= float(one['stamp']) < time_to:
                one['id'] = int(one['id'])
                one['num'] = float(one['num'])
                one['stamp'] = float(one['stamp'])
                temp.append(one)
            if float(one['stamp']) < time_from:
                break
        if point:
            t = mysql.get_order_history_time_th(time_from, point + 1)
            temp.extend(t)
        return temp
    except Exception, e:
        print e
        return []


def insert_cook_history(fid='', uid='', id=-1, stamp=0):
    if not(fid and stamp):
        return False

    try:
        key = r.get('cook_history_key')

        p = r.pipeline()
        p.lpush('cook_history', key)
        p.hmset('cook_history:%s' % key, {'fid': fid, 'uid': uid, 'id': id, 'stamp': stamp})
        p.incr('cook_history_key')
        p.execute()
        return True
    except Exception, e:
        print e
        return False


def get_cook_history(time_from, time_to):
    try:
        if time_from > time_to:
            return []
        temp = []
        keys = r.lrange('cook_history', 0, -1)

        point = None
        for key in keys:
            one = r.hgetall('cook_history:%s' % key)
            if not one:
                point = int(key)
                break
            if time_from <= float(one['stamp']) < time_to:
                one['id'] = int(one['id'])
                one['stamp'] = float(one['stamp'])
                temp.append(one)
            if float(one['stamp']) < time_from:
                break
        if point:
            t = mysql.get_cook_history_time_th(time_from, point + 1)
            temp.extend(t)
        return temp
    except Exception, e:
        print e
        return []


def insert_customer_history(session='', desk='', desk_uid='', stamp=0):
    if not(session and desk and desk_uid and stamp):
        return False

    try:
        key = r.get('customer_history_key')

        p = r.pipeline()
        p.lpush('customer_history')
        p.hmset('customer_history:%s' % key, {'session': session, 'desk': desk, 'desk_uid': desk_uid, 'stamp': stamp})
        p.incr('customer_history_key')
        p.execute()
        return True
    except Exception, e:
        print e
        return False


def get_customer_history(time_from, time_to):
    try:
        if time_from > time_to:
            return []
        temp = []
        keys = r.lrange('customer_history', 0, -1)

        point = None
        for key in keys:
            one = r.hgetall('customer_history:%s' % key)
            if not one:
                point = int(key)
                break
            if time_from <= float(one['stamp']) < time_to:
                one['stamp'] = float(one['stamp'])
                temp.append(one)
            if float(one['stamp']) < time_from:
                break
        if point:
            t = mysql.get_customer_history_time_th(time_from, point + 1)
            temp.extend(t)
        return temp
    except Exception, e:
        print e
        return []






def insert_cook_stat():
    pass


def get_cook_stat():
    pass


def insert_diet_stat():
    pass


def get_diet_stat():
    pass


def get_customer_visits(session, count=60000):
    num = 0
    keys = r.lrange('customer_history', 0, count)

    p = r.pipeline()
    for key in keys:
        p.hgetall('%s:%s' % ('customer_history', key))
    rows = p.execute()
    for row in rows:
        if row['session'] == session:
            num += 1
    return num

'''

'''
import time
t1 = time.clock()

r.set('key', 0)
p = r.pipeline()
for i in range(50000):
    p.rpush('test', i)

p.execute()
t2 = time.clock()

res = r.lrange('test', 0, 50000)
t3 = time.clock()
num = 0
for row in res:
    if int(row) == 9:
        num += 1
t4 = time.clock()
print t2-t1, t3-t2, t4-t3
print r.scan(match='test:*', count=8)

'''

