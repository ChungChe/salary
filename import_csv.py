#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys, traceback
from collections import defaultdict
from salary import *

employee_data = defaultdict(list)
employees = []
# name -> (date, on_time, off_time)s
def is_int(val):
    try:
        value = int(val)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} file_name".format(sys.argv[0]))
        sys.exit()

    with open(sys.argv[1]) as f:
        lines = f.readlines()
        lines.pop(0) # remove first line
    for line in lines:
        toks = line.split(',')
        # name, date, on_time, off_time 
        #print(toks[2],toks[3],toks[7], toks[8])
        name = toks[2].split()[0]
    
        employee_data[name].append((toks[3], toks[7], toks[8]))
        #m = employees(name=toks[2])
    print("employee count = {}".format(len(employee_data)))
    for name in employee_data:
        #print(key)
        m = employee(name)
        print("Employee: {}".format(name))
        print("--------------------------------------------")
        for data in employee_data[name]:
            date_num = int(data[0].split('/')[2]) # 2017/04/01
            
            m.set_working_data(date_num, data[1], data[2])
        m.round_data()
        m.get_salary()
        employees.append(m)


