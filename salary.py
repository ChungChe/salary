#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from var import *
#from peewee import *
# Use deferring initialization
#db = SqliteDatabase(None)

datetime_format = '%H:%M'

class employee:
    def __init__(self, name ='TEST', factor = 0.3333333, weight = 0.0, agency_fee = 2500, labor_insurance_fee = 1200, accommodation_fee = 2500):
        self.name = name
        self.factor = factor
        self.weight = weight
        self.on_work_time = 31 * [None] # preallocate time 
        self.off_work_time = 31 * [None] # preallocate time
        self.agency_fee = agency_fee
        self.labor_insurance_fee = labor_insurance_fee
        self.accommodation_fee = accommodation_fee
        self.gen_morning_test()
    def set_working_data(self, day, on_time, off_time): # day = 1 to 31
        self.on_work_time[day] = on_time
        self.off_work_time[day] = off_time
        
    def is_morning(self, day): # day = 1 to 31
        if self.on_work_time[day] == None:
            return None
        if self.off_work_time[day] == None:
            return None
        t1 = self.get_datetime(self.on_work_time[day])        
        if self.get_datetime('07:15') <= t1 <= self.get_datetime('16:45'):  
            return True
        return False
    def get_datetime(self, time_str):
        if time_str == None:
            return None
        return datetime.strptime(time_str, datetime_format)
    def gen_morning_test(self):
        for i in xrange(0, 30):
            self.set_working_data(i, '08:00', '17:00')
    def get_rest_hours(self, day): 
        flag = 0
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0
        t1 = self.get_datetime(self.on_work_time[day])        
        t2 = self.get_datetime(self.off_work_time[day])
        if t1 <= self.get_datetime('05:15') <= t2:  # through breakfirst
            flag += 1
        if t1 <= self.get_datetime('12:15') <= t2:  # through lunch
            flag += 2
        if t1 <= self.get_datetime('17:15') <= t2:  # through dinner
            flag += 4
        hours = 0.5 * bin(flag).count("1")
        return hours
    def get_working_hours(self, day):
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0
        rest_hours = self.get_rest_hours(day)
        t1 = self.get_datetime(self.on_work_time[day])        
        t2 = self.get_datetime(self.off_work_time[day]) - timedelta(hours=rest_hours)
        return (t2 - t1).total_seconds() / 3600.0
    def get_salary(self):
        total_sal = 0.0
        working_days_per_month = 0
        for day in xrange(0, 31):
            today_sal = 0.0
            isMor = self.is_morning(day)
            if isMor == None:
                continue
            sal_per_hour = base_sal_per_hour
            meal_fee = 0.0
            if isMor == True:
                meal_fee = breakfirst_fee
            elif isMor == False:
                meal_fee = lunch_fee 
                sal_per_hour += night_allowance_weight 
            hours = self.get_working_hours(day)
            today_hours = hours
            base_sal = 0.0
            if hours > 8.0: 
                hours -= 8.0
                base_sal += 8 * base_sal_per_hour
            else:
                base_sal += hours * base_sal_per_hour
                hours = 0.0
            overtime_1_sal = 0.0
            if hours > 2:
                hours -= 2.0
                overtime_1_sal += 2 * base_sal_per_hour * 1.33
            else:
                overtime_1_sal += hours * base_sal_per_hour * 1.33
                hours = 0.0
            overtime_2_sal = 0.0
            if hours > 0.0:
                overtime_2_sal += hours * base_sal_per_hour * 1.66
            today_sal += meal_fee + base_sal + overtime_1_sal + overtime_2_sal
            print("Day: {}, {} hrs, {} + {} + {} + {} = {}".format(day, today_hours, meal_fee, base_sal, overtime_1_sal, overtime_2_sal, today_sal))
            if today_sal != 0.0:
                working_days_per_month += 1
            total_sal += today_sal
        print("Working days = {}".format(working_days_per_month))
        final = total_sal - self.agency_fee - self.labor_insurance_fee - self.accommodation_fee
        print("Salary: {} - {} - {} - {} = {}".format(total_sal, self.agency_fee, self.labor_insurance_fee, self.accommodation_fee, final)) 
        return final

m = employee(name='GG', factor=0.5, weight=30)
print("Salary: {}".format(m.get_salary()))
