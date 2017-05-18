#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, traceback
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
        #self.gen_morning_test()
    # on: 7:54 -> 8:00
    # off: 8:07 -> 8:00
    # grid: 15 minutes
    def time_rounding(self, time, on_or_off):
        t1 = self.get_datetime('00:00')
        t2 = self.get_datetime(time)
        minutes = (t2 - t1).total_seconds() / 60.0 % 60
        if on_or_off:
            return (int(minutes + 14) / 15 * 15 ) % 60
        else:
            return (((int(minutes - 14) / 15) + 1) * 15 ) % 60
    def round_data(self):
        for day in xrange(0, 30):
            on_time = self.on_work_time[day]
            off_time = self.off_work_time[day]
            if on_time == None or len(on_time) == 0 or off_time == None or len(off_time) == 0:
                continue
            on_time_str = format(self.time_rounding(on_time, True),'02d')
            off_time_str = format(self.time_rounding(off_time, False),'02d')

            new_on_time_str = on_time.split(':')[0] + ':' + on_time_str
            new_off_time_str = off_time.split(':')[0] + ':' + off_time_str
            self.on_work_time[day] = new_on_time_str
            self.off_work_time[day] = new_off_time_str
        
    def set_working_data(self, day, on_time, off_time): # day = 1 to 31
        self.on_work_time[day] = on_time
        self.off_work_time[day] = off_time
    def is_morning_time(self, time):
        if self.get_datetime('17:30') <= time <= self.get_datetime('23:59'):  
            return False
        return True
        
    def is_morning(self, day): # day = 1 to 31
        on_work_day_str = self.on_work_time[day]
        if on_work_day_str == None or len(on_work_day_str) == 0:
            return None
        t1 = self.get_datetime(self.on_work_time[day])
        if t1 == None:
            return None
        return self.is_morning_time(t1)
    def get_datetime(self, time_str):
        try:
            if time_str == None or len(time_str) == 0:
                return None
        except Exception:
            print("Traceback !!")
            traceback.print_exc(file=sys.stdout)

        return datetime.strptime(time_str, datetime_format)
    def gen_morning_test(self):
        for i in xrange(0, 30):
            self.set_working_data(i, '17:00', '08:00')
    def get_rest_hours(self, day): 
        flag = 0
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0
        t1 = self.get_datetime(self.on_work_time[day])        
        t2 = self.get_datetime(self.off_work_time[day])
        if t1 < t2:
            if t1 <= self.get_datetime('05:15') <= t2:  # through breakfirst
                flag += 1
            if t1 <= self.get_datetime('12:15') <= t2:  # through lunch
                flag += 2
            if t1 <= self.get_datetime('17:15') <= t2:  # through dinner
                flag += 4
        else:
            if t1 >= self.get_datetime('05:15') >= t2:  # through breakfirst
                flag += 1
            if t1 >= self.get_datetime('12:15') >= t2:  # through lunch
                flag += 2
            if t1 >= self.get_datetime('17:15') >= t2:  # through dinner
                flag += 4

        hours = 0.5 * bin(flag).count("1")
        return hours
    def get_working_hours(self, day):
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0
        rest_hours = self.get_rest_hours(day)
        #print("rest: {}".format(rest_hours))
        t1 = self.get_datetime(self.on_work_time[day])        
        t2 = self.get_datetime(self.off_work_time[day]) - timedelta(hours=rest_hours)
        if t1 <= t2:
            return (t2 - t1).total_seconds() / 3600.0
        else:
            t3 = self.get_datetime('23:59') - t1;
            t4 = t2 - self.get_datetime('00:00')
            return (t3 + t4 + timedelta(minutes=1) - timedelta(hours=rest_hours)).total_seconds() / 3600.0


    def get_extra_bonus(self):
        if weight <= 0.0:
            return 0

    def get_salary(self):
        total_sal = 0.0
        working_days_per_month = 0
        for day in xrange(0, 31):
            today_sal = 0.0
            isMor = self.is_morning(day)
            if isMor == None:
                continue
            sal_per_hour = base_sal_per_hour
            hours = self.get_working_hours(day)
            
            meal_fee = 0.0
            if isMor == True:
                meal_fee = breakfirst_fee
            elif isMor == False:
                meal_fee = breakfirst_fee + dinner_fee 
                sal_per_hour += night_allowance_weight 
            
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
            print("Day: {} [{} - {}], {} hrs, {} + {} + {} + {} = {}".format(day, self.on_work_time[day], self.off_work_time[day], today_hours, meal_fee, base_sal, overtime_1_sal, overtime_2_sal, today_sal))
            if today_sal != 0.0:
                working_days_per_month += 1
            total_sal += today_sal
        if working_days_per_month <= 0:
            return 0
        print("Working days = {}".format(working_days_per_month))
        final = 0
        if total_sal > 0.0:
            final = total_sal - self.agency_fee - self.labor_insurance_fee - self.accommodation_fee
            print("Salary: {} - {} - {} - {} = {}".format(total_sal, self.agency_fee, self.labor_insurance_fee, self.accommodation_fee, final)) 
        return final
if __name__ == "__main__":
    m = employee(name='GG', factor=0.5, weight=30)
    print("Salary: {}".format(m.get_salary()))
