# coding=utf-8

import sqlite3
import os
import mysql
import myredis
import util
import time
import cPickle as pickle



company_file = 'company_info'
#company_info = None

with open(company_file, 'rb') as f:
    company_info = pickle.load(f)

db = mysql.db
get_category = mysql.get_category
get_diet = mysql.get_diet
get_faculty = mysql.get_faculty
get_role = mysql.get_role

get_desks = mysql.get_desks
insert_desk = mysql.insert_desk
delete_desk = mysql.delete_desk

desks = get_desks()
print desks

def check_desk(desk):
    try:
        global desks
        desk = desk.upper()
        if desk in desks:
            return True
        return False
    except Exception, e:
        print e
        return False


def insert(table, row):
    if table in ('diet', 'category', 'faculty'):
        mysql.insert(table, row)
    else:
        myredis.insert(table, row)


def delete(table, row):
    if table in ('diet', 'category', 'faculty'):
        mysql.delete(table, row)
    else:
        myredis.delete(table, row)



def get(table, time_from, time_to):
    if table in ('diet', 'category', 'faculty'):
        res = mysql.get(table, time_from, time_to)
    else:
        res = myredis.get(table, time_from, time_to)
    return res


def get_all(table):
    if table in ('diet', 'category', 'faculty'):
        res = mysql.get_all(table)
    else:
        res = myredis.get_all(table)
    return res


def get_comment(start, count=50000):
    res = myredis.get_comment(start, count)

    return res


#from order_history
def get_customer_visits(customer):
    return myredis.get_customer_visits(customer)


def diet_statistics(time_from, time_to, rows=None):
    if rows is None:
        rows = get('order_history', time_from, time_to)
    statistics = {}
    for diet in get_diet():
        key = int(diet['id'])
        statistics[key] = {'id': key, 'name': diet['name'], 'price': diet['price'], 'num': 0}
    for row in rows:
        key = int(row['id'])
        statistics[key]['num'] += float(row['num'])
    total = 0
    for row in statistics.values():
        total += float(row['price']) * float(row['num'])
    return total, statistics

#from cook_history
def cook_statistics(time_from, time_to, rows=None):
    if rows is None:
        rows = get('cook_history', time_from, time_to)
    statistics = {}
    mydiet = {}

    for i in get_diet():
        key = int(i['id'])
        mydiet[key] = i

    for cook in get_role('cook'):
        fid = cook['id']
        statistics[fid] = {'fid': fid, 'name': cook['name'], 'num': 0, 'val': 0}

    for row in rows:
        fid = row['fid']
        diet_id = int(row['id'])
        statistics[fid]['num'] += mydiet[diet_id]['base']
        statistics[fid]['val'] += mydiet[diet_id]['base'] * mydiet[diet_id]['price']

    total = 0
    for i in statistics.values():
        total += i['val']
    return total, statistics


# divide duration by month
def trend_statistics(count=12):

    diet_stat = mysql.get_diet_stat(count)
    cook_stat = mysql.get_cook_stat(count)
    res = {'diet_stat': diet_stat, 'cook_stat': cook_stat}
    return res


#last_update_stat = '2015.01.01'


def update_stat():
    global last_update_stat
    now = time.time()

    if now < util.strtostamp(util.next_month(last_update_stat)):
        return False
    end = util.strtostamp(util.first_day(now))
    print end
    time_from = util.strtostamp(last_update_stat)
    time_to = util.strtostamp(util.next_month(time_from))
    while time_to <= end:
        #update diet_stat
        diet_stat = diet_statistics(time_from, time_to)
        stat = diet_stat[1]
        for row in stat.values():
            row['stamp_from'] = util.stamptostr(time_from)
            row['stamp_to'] = util.stamptostr(time_to)
            myredis.insert('diet_stat', row)
        #update cook_stat
        cook_stat = cook_statistics(time_from, time_to)
        stat = cook_stat[1]
        for row in stat.values():
            row['stamp_from'] = util.stamptostr(time_from)
            row['stamp_to'] = util.stamptostr(time_to)
            myredis.insert('cook_stat', row)

        time_from = time_to
        time_to = util.strtostamp(util.next_month(time_from))













