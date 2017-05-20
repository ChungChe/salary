#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys, traceback
from collections import defaultdict
from salary import *

employee_working_data = defaultdict(list)
employees = []
# name -> (date, on_time, off_time)s

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: {} file_name".format(sys.argv[0]))
		sys.exit()
	employee_lines = []
	hire_date_data = defaultdict(str) 
	with open('employee.csv') as f:
		employee_lines = f.readlines()
		employee_lines.pop(0)
		for line in employee_lines:
			toks = line.split(',')
			name_toks = toks[2].split(' ')
			if len(name_toks) == 2:
				name = name_toks[0]
			else:
				continue
			hire_date = toks[8]
			#print("name: {}, hire_date: {}".format(name, hire_date))
			hire_date_data[name] = hire_date
	with open(sys.argv[1]) as f:
		lines = f.readlines()
		lines.pop(0) # remove first line
		if len(lines) > 0:
			date = lines[0].split(',')[3].split('/') # 2017/04/01
			year = date[0]
			month = date[1]
		for line in lines:
			toks = line.split(',')
			# name, date, on_time, off_time 
			#print(toks[2],toks[3],toks[7], toks[8])
			if len(toks[2].split()) != 2:
				continue
			name = toks[2].split()[0]
		
			employee_working_data[name].append((toks[3], toks[7], toks[8]))
			#m = employees(name=toks[2])
		print("employee count = {}".format(len(employee_working_data)))
		for name in employee_working_data:
			#print(key)
			m = employee(name, hire_date_data[name])
			
			print("Employee: {}, hire date: {}".format(name, hire_date_data[name]))
			for data in employee_working_data[name]:
				date_num = int(data[0].split('/')[2]) # 2017/04/01
				
				m.set_working_data(date_num, data[1], data[2])
			m.round_data()
			m.get_salary(year, month)
			employees.append(m)
			print("--------------------------------------------")


