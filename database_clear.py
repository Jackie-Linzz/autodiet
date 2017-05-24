# coding=utf-8
from myredis import r
from mysql import db
from mydatabase import insert
import util



categories = ({'id': 1, 'name': '凉菜', 'ord': 1, 'description': '', 'picture': ''},
              {'id': 3, 'name': '主食', 'ord': 3, 'description': '', 'picture': ''})

diet = [{'id': 1, 'name': '宫保鸡丁', 'price': 26, 'cid': 3, 'ord': 3, 'picture': '', 'base': 1, 'description': '', },
        {'id': 2, 'name': '状元养生炖', 'price': 26, 'cid': 3, 'ord': 3, 'picture': '', 'base': 1, 'description': '', },
        {'id': 3, 'name': '花生米', 'price': 26, 'cid': 1, 'ord': 1, 'picture': '', 'base': 0.5, 'description': '', },
        {'id': 4, 'name': '海带', 'price': 26, 'cid': 1, 'ord': 1, 'picture': '', 'base': 1, 'description': '', }]


faculty = [{'id': '0001', 'name': 'jackie', 'role': 'founder', 'password': 'root'},
           {'id': '0002', 'name': 'manager', 'role': 'manager', 'password': 'manager'},
           {'id': '0003', 'name': 'waiter', 'role': 'waiter', 'password': 'waiter'},
           {'id': '0004', 'name': 'cook', 'role': 'cook', 'password': 'cook'},
           {'id': '0005', 'name': '5', 'role': 'cook', 'password': 'cook'}]

order_history = [{'one_uid': '1', 'id': 1, 'desk_uid': '1', 'num': 1, 'stamp': util.strtostamp('2015.1.8')},
                 {'one_uid': '2', 'id': 2, 'desk_uid': '1', 'num': 1, 'stamp': util.strtostamp('2015.1.8')},
                 {'one_uid': '3', 'id': 3, 'desk_uid': '3', 'num': 0.5, 'stamp': util.strtostamp('2015.2.8')},
                 {'one_uid': '4', 'id': 4, 'desk_uid': '4', 'num': 1, 'stamp': util.strtostamp('2015.3.8')}]

customer_history = [{'session': 'a', 'desk': '1', 'desk_uid': '1', 'stamp': util.strtostamp('2015.1.8')},
                    {'session': 'b', 'desk': '2', 'desk_uid': '3', 'stamp': util.strtostamp('2015.2.8')},
                    {'session': 'c', 'desk': '1', 'desk_uid': '4', 'stamp': util.strtostamp('2015.3.8')}]

cook_history = [{'fid': '0004', 'uid': '1', 'id': 1, 'stamp': util.strtostamp('2015.1.8')},
                {'fid': '0004', 'uid': '2', 'id': 2, 'stamp': util.strtostamp('2015.1.8')},
                {'fid': '0005', 'uid': '3', 'id': 3, 'stamp': util.strtostamp('2015.2.8')},
                {'fid': '0005', 'uid': '4', 'id': 4, 'stamp': util.strtostamp('2015.3.8')}]

comment = [{'session': 'ss', 'comment': 'ssss', 'stamp': util.strtostamp('2015.1.8')}]

#diet_stat = [{'id': 1, 'name': 'ss', 'price': 88, 'num': 1, 'stamp_from': time.time(), 'stamp_to': time.time()}]
#cook_stat = [{'fid': 'ff', 'name': 'dd', 'num': 1, 'val': 88, 'stamp_from': time.time(), 'stamp_to': time.time()}]


def flush():
    r.flushdb()
    for table in ('category', 'diet', 'faculty', 'cook_history', 'customer_history', 'order_history', 'comment', 'diet_stat', 'cook_stat'):
        db.execute('delete from %s' % table)


def setup():

    r.setnx('order_history_th', 1)
    r.setnx('customer_history_th', 1)
    r.setnx('cook_history_th', 1)
    r.setnx('comment_th', 1)
    r.setnx('diet_stat_th', 1)
    r.setnx('cook_stat_th', 1)

    for i in diet:
        insert('diet', i)

    for i in categories:
        insert('category', i)

    for i in faculty:
        insert('faculty', i)

    for i in order_history:
        insert('order_history', i)
    for i in customer_history:
        insert('customer_history', i)
    for i in cook_history:
        insert('cook_history', i)
    for i in comment:
        insert('comment', i)

flush()
setup()