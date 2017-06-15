#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS 
from gevent.wsgi import WSGIServer

from xls2csv import *
from import_csv import *
from var import *
import os
#from collections import OrderedDict
from peewee import *

print("Init DB...")
db = SqliteDatabase(None)

class item(Model):
    name = CharField()
    hire_date = CharField()
    agency_fee = IntegerField() 
    labor_fee = IntegerField()
    insurance_fee = IntegerField()
    borrowing = IntegerField()
    unpaid = IntegerField()
    accommodation_fee = IntegerField()
    factor = DoubleField()
    weight = DoubleField()
    class Meta:
        database = db

def create_or_load_db(n, hire_date = '', agency_fee = 1500, labor_fee = 399, insurance_fee = 296, borrowing = 0, unpaid = 0, accommodation_fee = 0, factor = 0.0, weight = 0.0):
    try:
        lst = item.select().where(item.name == n).get()
        return lst._data
    except item.DoesNotExist:
        print("Not Found, create")
        item.create(name = n,
                hire_date = hire_date,
                agency_fee = agency_fee,
                labor_fee = labor_fee,
                insurance_fee = 296,
                borrowing = borrowing,
                unpaid = unpaid,
                accommodation_fee = accommodation_fee,
                factor = factor,
                weight = weight)
        lst = item.select().where(item.name == n).get()
        return lst._data

def get_factor_n_weight(name):
    factor = 0.0
    weight = 0.0
    if name in special_bonus:
        factor = special_bonus[name][0]
        weight = special_bonus[name][1]
    return {'factor': factor, 'weight': weight}


#print(dic_list)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['UPLOADED_PHOTOS_DEST'] = app.static_folder


gg = UploadSet('test', DOCUMENTS,
        default_dest=lambda app: app.static_folder)

configure_uploads(app, gg)
@app.route('/save', methods=['GET', 'POST'])
def save():
    print("Save")
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'upload' in request.files:
        filename = gg.save(request.files['upload'])
        full_path_file = '{}/{}'.format(app.static_folder, filename)
        xls2csv('{}/{}'.format(app.static_folder, filename), 'tmp.csv')
        output = parse_csv('tmp.csv')
        
        overtime_headers = []
        overtime_headers.append({'name': 'name', 'label': '姓名', 'datatype': 'string', 'editable': False})
        overtime_headers.append({'name': 'stage_num', 'label': '發放階段', 'datatype': 'integer', 'editable': False})
        overtime_headers.append({'name': 'base_working_days', 'label': '基本工作天', 'datatype': 'integer', 'editable': True})
        overtime_headers.append({'name': 'morning_working_days', 'label': '早班天', 'datatype': 'integer', 'editable': True})
        overtime_headers.append({'name': 'night_working_days', 'label': '晚班天', 'datatype': 'integer', 'editable': True})
        overtime_headers.append({'name': 'total_overtime_hrs', 'label': '加班1', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
        overtime_headers.append({'name': 'total_overtime1_hrs', 'label': '加班133', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
        overtime_headers.append({'name': 'total_overtime2_hrs', 'label': '加班166', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
        overtime_headers.append({'name': 'total_nig_hours', 'label': '夜津時數', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
        overtime_headers.append({'name': 'total_night_sal', 'label': '夜津加給', 'datatype': 'double($, 0, dot, comma, 1)', 'editable': True})
        overtime_headers.append({'name': 'overtime_salary', 'label': '總加班費', 'datatype': 'double($, 0, dot, comma, 1)', 'editable': False})
        
        overtime_data = []
        count = 1
        # gather two_week_lst
        for o in output:
            #print(o)
            weeks = []
            try:
                weeks = o['two_week_lst']
            except Exception as e:
                print('Error: {}'.format(e))
                continue
            #print("len of weeks: {}".format(len(weeks)))
            #print(o['two_week_lst'])
            #print("Name: {}".format(o['name']))
            for d in weeks:

                overtime_data.append({'id': count, 'values': {'name': o['name'], 
                        'stage_num': d['stage_num'], 
                        'base_working_days': d['base_working_days'], 
                        'morning_working_days': d['morning_working_days'], 
                        'night_working_days': d['night_working_days'], 
                        'total_overtime_hrs': d['total_overtime_hrs'],
                        'total_overtime1_hrs': d['total_overtime1_hrs'],
                        'total_overtime2_hrs': d['total_overtime2_hrs'],
                        'total_nig_hours': d['total_nig_hours'],
                        'total_night_sal': d['total_night_sal'],
                        'overtime_salary': d['overtime_salary']}})
                count += 1
        
        overtime_dict = {'metadata': overtime_headers, 'data': overtime_data}
        # remove the file
        os.remove(full_path_file)
        return render_template('display.html', backend_data=output, test=overtime_dict)
    # load or create empolyee info
    headers = []
    headers.append({'name': 'name', 'label': '姓名', 'datatype': 'string', 'editable': False})
    headers.append({'name': 'hire_date', 'label': '到職日', 'datatype': 'string', 'editable': False})
    headers.append({'name': 'agency_fee', 'label': '仲介費', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'labor_fee', 'label': '勞保費', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'insurance_fee', 'label': '健保費', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'borrowing', 'label': '借金', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'unpaid', 'label': '未給付', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'accommodation_fee', 'label': '食宿費', 'datatype': 'integer($,, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'factor', 'label': '指數', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
    headers.append({'name': 'weight', 'label': '權重', 'datatype': 'double(,2, dot, comma, 1)', 'editable': True})
    dict_list = []
    table_count = 1
    for rec in item.select():
        tmp_dic = rec._data
        dict_list.append({'id': table_count, 'values': tmp_dic})
        table_count += 1
    final = {'metadata': headers, 'data': dict_list}
    return render_template('index.html', data = final)

def init():
    employee_names = get_employee_names('employee.csv')
    hire_date_data = get_employee_hire_date_data('employee.csv')

    db.init('employee.db')
    try:
        item.create_table()
    except Exception as e:
        print(e)

    for n in employee_names:
        fw_dic = get_factor_n_weight(n)
        print('Name: {}'.format(n))
        create_or_load_db(n, hire_date = hire_date_data[n], factor = fw_dic['factor'], weight = fw_dic['weight'])

def run_server():
    http_server = WSGIServer(('', 9453), app)
    http_server.serve_forever()

if __name__ == '__main__':
    init()
    run_server()
