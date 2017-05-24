import time
import datetime
import re
import calendar

time_format = '%Y.%m.%d'


def strtostamp(now):
    return time.mktime(time.strptime(now, '%Y.%m.%d'))


def stamptostr(stamp):
    return time.strftime('%Y.%m.%d', time.localtime(stamp))


def first_day(stamp):
    if isinstance(stamp, float):
        stamp = stamptostr(stamp)
    r = re.compile(r'^([0-9]{4})\.([0-9]{2}|[0-9])\.([0-9]{2}|[0-9])$')
    match = r.match(stamp)
    year = match.group(1)
    month = match.group(2)
    day = '01'
    return '%s.%s.%s' % (year, month, day)


#'year.month.day'
def next_month(now):
    if isinstance(now, float):
        now = stamptostr(now)
    r = re.compile(r'^([0-9]{4})\.([0-9]{2}|[0-9])\.([0-9]{2}|[0-9])$')
    match = r.match(now)
    if match is None:
        return -1
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    if not (0 <= month <= 12):
        return -1
    range_flag = day == calendar.monthrange(year, month)[1]
    month_next = month + 1
    year_next = year
    if month_next == 13:
        year_next = year + 1
        month_next = 1
    month_range = calendar.monthrange(year_next, month_next)[1]
    day_next = day
    if day < 1:
        day_next = 1
    if day > month_range:
        day_next = month_range
    if range_flag:
        day_next = month_range

    return '%s.%s.%s' % (year_next, month_next, day_next)


def next_day(now):
    now = time.strptime('%Y.%m.%d', now)
    t = now + datetime.timedelta(days=1)
    return time.strftime('%Y.%m.%d', t)


#return [(stamp, stamp), (stamp, stamp)]
def divided_by(time_from, time_to, interval='month'):
    temp = []
    if interval == 'month':
        start = time_from
        while True:
            start_next = strtostamp(next_month(stamptostr(start)))
            if start_next > time_to:
                temp.append((start, time_to))
                break
            else:
                temp.append((start, start_next))
                start = start_next
        return temp
    return []

'''
time_from = strtostamp('2015.1.31')
time_to = strtostamp('2015.6.2')

res = divided_by(time_from, time_to)
t = []
for row in res:
    t.append((stamptostr(row[0]), stamptostr(row[1])))
print res
print t

'''







