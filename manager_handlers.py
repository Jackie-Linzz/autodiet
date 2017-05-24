#coding=utf-8
import tornado.web
import tornado.httputil
import functools
import cPickle as pickle
import uuid
import os
import time
import mydata
import mydatabase
import qrcode
import tarfile


from tornado.escape import json_decode, json_encode

company_file = mydatabase.company_file


def manager_auth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        who = self.get_secure_cookie('who', None)
        if who != 'manager':
            response = {'status': 'denied', 'next': '/'}
            self.finish(json_encode(response))
            return
        return method(self, *args, **kwargs)
    return wrapper


class ManagerHandler(tornado.web.RequestHandler):
    #@manager_auth
    def get(self):
        self.render('manager.html')


class CompanyInfoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('company-info.html')

    def post(self):
        name = json_decode(self.get_argument('name'))
        short_name = json_decode(self.get_argument('shortname'))
        location = json_decode(self.get_argument('location'))
        desc = json_decode(self.get_argument('desc'))
        welcome = json_decode(self.get_argument('welcome'))
        info = {'name': name, 'shortname': short_name, 'location': location, 'desc': desc, 'welcome': welcome}
        mydatabase.company_info = info
        global company_file
        with open(company_file, 'wb') as f:

            pickle.dump(info, f)
        response = mydatabase.company_info
        response['status'] = 'ok'
        self.write(json_encode(response))


class CompanyDataHandler(tornado.web.RequestHandler):
    def post(self):
        global company_file

        response = mydatabase.company_info
        response['status'] = 'ok'
        self.write(json_encode(response))


class CategoryAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('category-add.html')

    def post(self):
        #attention to type
        cid = self.get_argument('id', None)
        name = self.get_argument('name', None)
        order = self.get_argument('order', None)
        desc = self.get_argument('desc', None)
        picture = ''
        print self.request.files
        if self.request.files:
            file_metas = self.request.files['picture']
            print file_metas
            upload_path = os.path.join(os.path.dirname(__file__), 'static/pictures')
            for file_meta in file_metas:
                file_name = file_meta['filename']
                content = file_meta['body']
                suffix = os.path.splitext(file_name)[-1]
                picture = str(uuid.uuid4()) + suffix

                full_path = os.path.join(upload_path, picture)
                with open(full_path, 'wb') as f:
                    f.write(content)
        #store in database

        try:
            mydatabase.insert('category', {'id': cid, 'name': name, 'ord': order, 'description': desc, 'picture': picture})
        except Exception, e:
            if picture:
                os.remove(os.path.join(os.path.dirname(__file__), 'static/pictures/' + picture))

        mydata.categories = mydatabase.get_category()
        self.render('category-add.html')


class CategoryManageHandler(tornado.web.RequestHandler):
    def get(self):
        response = {'status': 'ok', 'categories': mydata.categories}
        self.write(json_encode(response))

    def post(self):
        cid = json_decode(self.get_argument('cid'))
        db = mydatabase.db
        rows = db.query('select * from category where id = %s' % cid)
        row = rows[0]
        if row['picture']:
            picture_path = os.path.dirname(__file__) + '/static/pictures/' + row['picture']
            os.remove(picture_path)
        mydatabase.delete('category', row)
        mydata.categories = mydatabase.get_category()

        response = {'status': 'ok', 'categories': mydata.categories}
        self.write(json_encode(response))


class DietAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('diet-add.html')

    def post(self):

        #attention to variable type
        diet_id = int(self.get_argument('id'))
        name = self.get_argument('name')
        price = float(self.get_argument('price'))
        base = float(self.get_argument('base'))
        cid = int(self.get_argument('cid'))
        order = int(self.get_argument('order'))
        desc = self.get_argument('desc')
        picture = ''
        print self.request.files
        if self.request.files:
            metas = self.request.files['picture']
            for meta in metas:
                print meta
                file_name = meta['filename']
                content = meta['body']
                ext = os.path.splitext(file_name)[-1]
                picture = str(uuid.uuid4()) + ext
                full_path = os.path.join(os.path.dirname(__file__), 'static/pictures/' + picture)
                with open(full_path, 'wb') as f:
                    f.write(content)
        # store into database

        try:
            mydatabase.insert('diet', {'id': diet_id, 'name': name, 'price': price, 'base': base, 'cid': cid, 'ord': order, 'description': desc, 'picture': picture})
        except Exception, e:
            if picture:
                os.remove(os.path.join(os.path.dirname(__file__), 'static/pictures/' + picture))

        mydata.diet = mydatabase.get_diet()
        self.render('diet-add.html')


class DietManageHandler(tornado.web.RequestHandler):
    def get(self):
        response = {'status': 'ok', 'diet': mydata.diet}
        self.write(json_encode(response))

    def post(self):
        diet_id = json_decode(self.get_argument('id'))

        rows = mydatabase.db.query('select * from diet where id=%s' % diet_id)
        row = rows[0]
        if row['picture']:
            picture_path = os.path.dirname(__file__) + '/static/pictures/' + row['picture']
            print picture_path
            os.remove(picture_path)
        mydatabase.delete('diet', row)
        mydata.diet = mydatabase.get_diet()
        response = {'status': 'ok', 'diet': mydata.diet}
        self.write(json_encode(response))


class DeskAddHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        desk = json_decode(self.get_argument('desk'))
        desk = desk.upper()
        desks = mydatabase.desks
        if desk not in desks:
            path = os.path.dirname(__file__) + '/static/desks/' + desk + '.png'
            img = qrcode.make(desk)
            img.save(path)
            mydatabase.insert_desk(desk)
            desks.append(desk)
            desks.sort()

        response = {'status': 'ok', 'desks': desks}
        self.write(json_encode(response))


class DeskManageHandler(tornado.web.RequestHandler):
    def get(self):
        mydatabase.desks = mydatabase.get_desks()
        response = {'status': 'ok', 'desks': mydatabase.desks}
        self.write(json_encode(response))

    def post(self):
        desk = json_decode(self.get_argument('desk'))
        desks = mydatabase.desks
        if desk in desks:
            path = os.path.dirname(__file__) + '/static/desks/' + desk + '.png'
            os.remove(path)
            desks.remove(desk)
            mydatabase.delete_desk(desk)
        response = {'status': 'ok', 'desks': desks}
        self.write(json_encode(response))


class QrcodeDownloadHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=qrcode.tar')
        dir_path = os.path.dirname(__file__) + '/static/desks'
        files = []
        for d, s, f in os.walk(dir_path):
            files.extend(f)
        tar_path = dir_path + '/qrcode.tar'
        out = tarfile.open(tar_path, 'w')
        try:
            for f in files:

                full_path = dir_path + '/' + f
                out.add(full_path)
        finally:
            out.close()
        with open(tar_path, 'rb') as f:
            self.write(f.read())





class FacultyAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('faculty-add.html')

    def post(self):

        fid = str(self.get_argument('id')).strip()
        name = str(self.get_argument('name')).strip()
        role = str(self.get_argument('role')).strip()
        password = str(self.get_argument('password')).strip()
        #inset into database

        try:
            mydatabase.insert('faculty', {'id': fid, 'name': name, 'role': role, 'password': password})
        except Exception, e:
            print e

        self.render('faculty-add.html')


class FacultyManageHandler(tornado.web.RequestHandler):
    def get(self):

        response = {'status': 'ok', 'faculty': mydatabase.get_faculty()}
        self.write(json_encode(response))

    def post(self):
        fid = json_decode(self.get_argument('id')).strip()
        print fid, type(fid)

        try:
            mydatabase.delete('faculty', {'id': fid})

        except Exception, e:
            print e

        faculty = mydatabase.get_faculty()
        response = {'status': 'ok', 'faculty': faculty}
        self.write(json_encode(response))


class HistoryDataHandler(tornado.web.RequestHandler):
    def post(self):
        year_from = json_decode(self.get_argument('year_from'))
        month_from = json_decode(self.get_argument('month_from'))
        day_from = json_decode(self.get_argument('day_from'))
        year_to = json_decode(self.get_argument('year_to'))
        month_to = json_decode(self.get_argument('month_to'))
        day_to = json_decode(self.get_argument('day_to'))

        time_from = str(year_from) + ' ' + str(month_from) + ' ' + str(day_from)
        time_to = str(year_to) + ' ' + str(month_to) + ' ' + str(day_to)
        time_from = time.strptime(time_from, '%Y %m %d')
        time_to = time.strptime(time_to, '%Y %m %d')
        time_from = time.mktime(time_from)
        time_to = time.mktime(time_to)

        diet_stat = mydatabase.diet_statistics(time_from, time_to)
        cook_stat = mydatabase.cook_statistics(time_from, time_to)
        trend_stat = mydatabase.trend_statistics(12)
        response = {'status': 'ok', 'diet_stat': diet_stat, 'cook_stat': cook_stat, 'trend_stat': trend_stat}
        self.finish(json_encode(response))




