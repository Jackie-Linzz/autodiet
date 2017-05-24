# coding=utf-8
import MySQLdb


import mytorndb
'''
conn = MySQLdb.connect(host='localhost', port=3306, user='autodiet', passwd='autodiet', db='autodiet', charset='utf8')
cursor = conn.cursor()
'''
db = mytorndb.Connection('127.0.0.1:3306', 'autodiet', user='autodiet', password='autodiet2')
#db.insert_by_dict('comment', {'th': 1, 'session': '1', 'comment': 'I like it'})


#print db.executemany_rowcount('insert into comment (th, comment) values (%s, %s)', [(13, 'delicious'), (14, 'great')])
def insert(table, row):
    global db
    db.insert_dict(table, row)


def insert_many(table, rows):
    global db
    return db.insert_many_dict(table, rows)


def delete(table, row):
    global db
    condition = []
    for key in row.keys():
        if isinstance(row[key], (str, unicode)):
            condition.append('%s = "%s"' % (key, row[key]))
        else:
            condition.append('%s = %s' % (key, row[key]))

    condition = ' and '.join(condition)
    if table == 'faculty':
        db.execute('delete from %s where %s' % (table, condition))
    if table in ('diet', 'category'):
        db.execute('delete from %s where %s' % (table, condition))
    if table in ('comment', 'cook_history', 'order_history', 'customer_history', 'diet_stat', 'cook_stat'):
        db.execute('delete from %s where %s' % (table, condition))


def get_all(table):
    global db
    return db.query('select * from %s' % table)


def get(table, time_from, time_to):
    global db
    return db.query('select * from %s where %s <= stamp < %s' % (table, time_from, time_to))


def get_history(table, time_from, time_to):
    global db
    return db.query('select * from %s where %s <= stamp < %s' % (table, time_from, time_to))


def get_category():
    return get_all('category')


def get_diet():
    return get_all('diet')


def get_faculty():
    return get_all('faculty')


def get_role(role):
    global db
    return db.query('select * from faculty where role = "%s" ' % role)


def get_diet_stat(count=6):
    global db
    temp = db.query('select stamp_from, sum(price * num) as vals from diet_stat group by stamp_from order by stamp_from desc limit %s' % count)
    temp.reverse()
    return temp


def get_cook_stat(count=6):
    global db
    temp = db.query('select stamp_from, sum(val) as vals from cook_stat group by stamp_from order by stamp_from desc limit %s' % count)
    temp.reverse()
    return temp


def insert_desk(desk):
    desk = desk.upper()
    insert('desks', {'desk': desk})


def delete_desk(desk):
    global db
    desk = desk.upper()
    db.execute('delete from desks where desk = %s' % desk)


def get_desks():
    global db
    temp = db.query('select * from desks')
    res = []
    for row in temp:
        res.append(row['desk'])
    res.sort()
    return res
'''
categories = ({'id': 1, 'name': '凉菜', 'ord': 1, 'description': '', 'picture': ''},
              {'id': 3, 'name': '主食', 'ord': 3, 'description': '', 'picture': ''})

diet = [{'id': 1, 'name': '宫保鸡丁', 'price': 26, 'cid': 3, 'ord': 3, 'picture': '', 'base': 1, 'description': '', },
        {'id': 2, 'name': '状元养生炖', 'price': 26, 'cid': 3, 'ord': 3, 'picture': '', 'base': 1, 'description': '', },
        {'id': 3, 'name': '花生米', 'price': 26, 'cid': 1, 'ord': 1, 'picture': '', 'base': 1, 'description': '', },
        {'id': 4, 'name': '海带', 'price': 26, 'cid': 1, 'ord': 1, 'picture': '', 'base': 1, 'description': '', }]


faculty = [{'id': '0001', 'name': 'jackie', 'role': 'founder', 'password': 'root'},
           {'id': '0002', 'name': 'manager', 'role': 'manager', 'password': 'manager'},
           {'id': '0003', 'name': 'waiter', 'role': 'waiter', 'password': 'waiter'},
           {'id': '0004', 'name': 'cook', 'role': 'cook', 'password': 'cook'}]

sql1 = 'insert into category (id, name, ord, description, picture) values (%s, %s, %s, %s, %s)'
sql2 = 'insert into diet (id,name,price,cid,ord,picture,base,description) values (%s,%s,%s,%s,%s,%s,%s,%s)'
sql3 = 'insert into faculty (id, name, role, password) values (%s,%s,%s,%s)'
print 'inserting data'
for i in categories:
    cursor.execute(sql1, (i['id'], i['name'], i['order'], i['desc'], i['picture']))

for i in diet:
    print i.values()
    cursor.execute(sql2, (i['id'], i['name'], i['price'], i['cid'], i['order'], i['picture'], i['base'], i['desc']))

for i in faculty:
    print i.values()
    cursor.execute(sql3, (i['id'], i['name'], i['role'], i['password']))

conn.commit()

cursor.execute('select * from category')
for i in cursor.fetchall():
    print i
'''

'''
def insert_category(id=-1, name='', order='', desc='', picture=''):
    global conn, cursor
    try:
        cursor.execute('insert into category (id, name, ord, description, picture) values (%s,%s,%s,%s,%s)',
                       (id, name, order, desc, picture))
        conn.commit()
    except Exception, e:
        return False
    else:
        return True


def get_category():
    global cursor
    temp = []
    cursor.execute('select id, name, ord, description, picture from category')
    for row in cursor.fetchall():
        temp.append({'id': row[0], 'name': row[1], 'order': row[2],
                     'desc': row[3], 'picture': row[4]})
    temp.sort(key=lambda x: x['order'])
    return temp


def insert_diet(id=-1, name='', price='', cid='', order='', picture='', base='', desc=''):
    global conn, cursor
    try:
        cursor.execute('insert into diet (id, name, price, cid, ord, picture, base, description)',
                       (id, name, price, cid, order, picture, base, desc))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_diet():
    global cursor
    temp = []
    cursor.execute('select id, name, price, cid, ord, picture, base, description from diet')
    for row in cursor.fetchall():
        temp.append({'id': row[0], 'name': row[1], 'price': row[2], 'cid': row[3],
                     'order': row[4], 'picture': row[5], 'base': row[6], 'desc': row[7]})
    temp.sort(key=lambda x: x['order'])
    return temp


def insert_faculty(id='', name='', role='', password=''):
    global cursor, conn
    try:
        cursor.execute('insert into faculty (id, name, role, password) values (%s,%s,%s,%s)', (id, name, role, password))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_faculty():
    global cursor
    try:
        temp = []
        cursor.execute('select id, name, role, password from faculty')
        for row in cursor.fetchall():
            temp.append({'id': row[0], 'name': row[1], 'role': row[2], 'password': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def get_role(role):
    global cursor
    try:
        temp = []
        cursor.execute('select id, name, role, password from faculty where role = "%s"' % role)
        for row in cursor.fetchall():
            temp.append({'id': row[0], 'name': row[1], 'role': row[2], 'password': row[3]})
        return temp
    except Exception, e:
        print e
        return []




#diet history


def insert_order_history(one_uid='', desk_uid='', id=-1, num=0, stamp=0):
    if not(one_uid and desk_uid and num):
        return False
    global conn, cursor
    try:
        cursor.execute('insert into order_history (one_uid,desk_uid,id,num,stamp) values (%s,%s,%s,%s,%s)',
                       (one_uid, desk_uid, id, num, stamp))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_order_history(time_from, time_to):
    global cursor
    temp = []
    try:
        cursor.execute('select one_uid,desk_uid,id,num,stamp from order_history where stamp between %s and %s', (time_from, time_to))
        for row in cursor.fetchall():
            temp.append({'one_uid': row[0], 'desk_uid': row[1], 'id': row[2], 'num': row[3], 'stamp': row[4]})
        return temp
    except Exception, e:
        print e
        return []


def get_order_history_th(th_from, th_to):
    global cursor
    temp = []
    try:
        cursor.execute('select one_uid,desk_uid,id,num,stamp from order_history where th between %s and %s -1', (th_from, th_to))
        for row in cursor.fetchall():
            temp.append({'one_uid': row[0], 'desk_uid': row[1], 'id': row[2], 'num': row[3], 'stamp': row[4]})
        return temp
    except Exception, e:
        print e
        return []


def get_order_history_time_th(time, th):
    global cursor
    temp = []
    try:
        cursor.execute('select one_uid,desk_uid,id,num,stamp from order_history where stamp >= %s and th < %s', (time, th))
        for row in cursor.fetchall():
            temp.append({'one_uid': row[0], 'desk_uid': row[1], 'id': row[2], 'num': row[3], 'stamp': row[4]})
        return temp
    except Exception, e:
        print e
        return []


def insert_cook_history(fid='', uid='', id=-1, stamp=0):
    if not(fid and stamp):
        return False
    global conn, cursor
    try:
        cursor.execute('insert into cook_history (fid, uid, id, stamp) values (%s,%s,%s)', (fid, uid, id, stamp))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_cook_history(time_from, time_to):
    global cursor
    try:
        temp = []
        cursor.execute('select fid,uid,id,stamp from cook_history where stamp between %s and %s', (time_from, time_to))
        for row in cursor.fetchall():
            temp.append({'fid': row[0], 'uid': row[1], 'id': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def get_cook_history_th(th_from, th_to):
    global cursor
    try:
        temp = []
        cursor.execute('select fid,uid,id,stamp from cook_history where th between %s and %s -1', (th_from, th_to))
        for row in cursor.fetchall():
            temp.append({'fid': row[0], 'uid': row[1], 'id': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def get_cook_history_time_th(time, th):
    global cursor
    try:
        temp = []
        cursor.execute('select fid,uid,id,stamp from cook_history where stamp >= %s and th < %s', (time, th))
        for row in cursor.fetchall():
            temp.append({'fid': row[0], 'uid': row[1], 'id': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def insert_customer_history(session='', desk='', desk_uid='', stamp=0):
    if not(session and desk and desk_uid and stamp):
        return False
    global conn, cursor
    try:
        cursor.execute('insert into customer_history (session,desk,desk_uid,stamp) values (%s,%s,%s,%s)',
                       (session, desk, desk_uid, stamp))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_customer_history(time_from, time_to):
    global cursor
    try:
        temp = []
        cursor.execute('select session,desk,desk_uid,stamp from customer_history where stamp between %s and %s', (time_from, time_to))
        for row in cursor.fetchall():
            temp.append({'session': row[0], 'desk': row[1], 'desk_uid': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def get_customer_history_th(th_from, th_to):
    global cursor
    try:
        temp = []
        cursor.execute('select session,desk,desk_uid,stamp from customer_history where th between %s and %s -1', (th_from, th_to))
        for row in cursor.fetchall():
            temp.append({'session': row[0], 'desk': row[1], 'desk_uid': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def get_customer_history_time_th(time, th):
    global cursor
    try:
        temp = []
        cursor.execute('select session,desk,desk_uid,stamp from customer_history where stamp >= %s and th < %s', (time, th))
        for row in cursor.fetchall():
            temp.append({'session': row[0], 'desk': row[1], 'desk_uid': row[2], 'stamp': row[3]})
        return temp
    except Exception, e:
        print e
        return []


def insert_comment(session='', comment=''):
    if not(session and comment):
        return False
    global conn, cursor
    try:
        cursor.execute('insert into comment (session, comment) values (%s,%s)', (session, comment))
        conn.commit()
        return True
    except Exception, e:
        print e
        return False


def get_comment(start, count):
    temp = []
    global conn, cursor
    try:
        cursor.execute('select session,comment from comment order by th desc limit %s, %s', (start, count))
        for row in cursor.fetchall():
            temp.append(row[0])
        return temp
    except Exception, e:
        print e
        return temp

'''



