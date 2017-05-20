#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, traceback
from datetime import datetime, timedelta
from var import *
import math
import calendar
#from peewee import *
# Use deferring initialization
#db = SqliteDatabase(None)

datetime_format = '%H:%M'

class employee:
    def __init__(self, name ='TEST', hire_date = '2017/01/01', factor = 0.3333333, weight = 0.0, agency_fee = 2500, labor_insurance_fee = 1200, accommodation_fee = 2500):
        self.name = name
        self.hire_date = hire_date
        self.factor = factor
        self.weight = weight
        self.on_work_time = 32 * [None] # preallocate time 
        self.off_work_time = 32 * [None] # preallocate time
        self.agency_fee = agency_fee
        self.labor_insurance_fee = labor_insurance_fee
        self.accommodation_fee = accommodation_fee
        #self.gen_morning_test()
    # on: 7:54 -> 8:00
    # off: 8:07 -> 8:00
    # grid: 15 minutes
    def time_rounding(self, time, on_or_off):
        grid = 15
        hr = int(time.split(':')[0])
        if on_or_off:
            if hr == 7 or hr == 19 or hr == 21:
                grid = 60
        else:
            if hr == 8 or hr == 20 or hr == 22:
                grid = 60
        t1 = self.get_datetime('00:00')
        t2 = self.get_datetime(time)
        minutes = (t2 - t1).total_seconds() / 60.0 % 60
        if on_or_off:
            # margin
            if hr == 8 or hr == 20 or hr == 22:
                if 0 <= minutes <= 5:
                    minutes = 0
            return (int(minutes + (grid - 1)) / grid * grid ) % 60
        else:
            return (((int(minutes - (grid - 1)) / grid) + 1) * grid ) % 60
    def round_data(self):
        for day in xrange(1, 32):
            on_time = self.on_work_time[day]
            off_time = self.off_work_time[day]
            
            if on_time == None or len(on_time) == 0 or off_time == None or len(off_time) == 0:
                continue
            
            if on_time == off_time:
                continue
            min_diff = (self.get_datetime(off_time) - self.get_datetime(on_time)).total_seconds() / 60.0
            if abs(min_diff) < 15:
                self.on_work_time[day] = on_time
                self.off_work_time[day] = on_time
                continue
            on_time_min = int(on_time.split(':')[1])
            off_time_min = int(off_time.split(':')[1])

            on_time_round_min = self.time_rounding(on_time, True)
            off_time_round_min = self.time_rounding(off_time, False)

            on_time_hr = int(on_time.split(':')[0])
            off_time_hr = int(off_time.split(':')[0])

            # inc on_time_hr
            margin = 5
            if on_time_round_min < on_time_min:
                if -margin <= on_time_round_min - on_time_min < 0:
                    pass
                else:
                    on_time_hr = (on_time_hr + 1) % 24 
            if off_time_round_min < off_time_min:
                off_time_hr = (off_time_hr + 1) % 24 
            
            on_time_min_str = format(on_time_round_min,'02d')
            off_time_min_str = format(off_time_round_min,'02d')
            
            new_on_time_str = format(on_time_hr, '02d') + ':' + on_time_min_str
            new_off_time_str = off_time.split(':')[0] + ':' + off_time_min_str

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

    def get_datetime_date(self, time_str):
        datetime_format = '%Y/%m/%d'
        if time_str == None or len(time_str) == 0:
            return None
        return datetime.strptime(time_str, datetime_format)

    def is_rest_day(self, time_str):
        t1 = self.get_datetime_date(time_str)
        t2 = self.get_datetime_date('2017/05/15')
        day_diff = abs((t1 - t2).total_seconds() / 60.0 / 60.0 / 24.0)
        if day_diff % 14 == 0:
            return True
        return False

    def gen_morning_test(self):
        for i in xrange(1, 32):
            self.set_working_data(i, '17:00', '08:00')
    def get_rest_hours(self, day): 
        flag = 0
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0

        t1 = self.get_datetime(self.on_work_time[day])        
        t2 = self.get_datetime(self.off_work_time[day])
        if t1 == None or t2 == None:
            return 0.0
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
        if self.on_work_time[day] == None or len(self.on_work_time[day]) == 0:
            return 0.0
        if self.off_work_time[day] == None or len(self.off_work_time[day]) == 0:
            return 0.0
        rest_hours = self.get_rest_hours(day)
        #print("rest: {}".format(rest_hours))
        t1 = self.get_datetime(self.on_work_time[day])
        t2 = self.get_datetime(self.off_work_time[day]) - timedelta(hours=rest_hours)
        if t1 == None or t2 == None:
            return 0.0
        if t1 <= t2:
            return (t2 - t1).total_seconds() / 3600.0
        else:
            t3 = self.get_datetime('23:59') - t1;
            t4 = t2 - self.get_datetime('00:00')
            return (t3 + t4 + timedelta(minutes=1)).total_seconds() / 3600.0
    def is_new_hire(self, year, month):
        hire_date = self.hire_date
        toks = hire_date.split('/')
        hire_year = int(toks[0])
        hire_month= int(toks[1])
        if int(year) == hire_year and int(month) == hire_month:
            return True
        return False
    def get_extra_bonus(self):
        if weight <= 0.0:
            return 0

    def get_salary(self, year, month):
        overtime_salary = 0.0
        working_days_per_month = 0
        morning_working_days = 0
        night_working_days = 0
        total_working_hours = 0
        total_days_in_this_month = calendar.monthrange(int(year), int(month))[1]
        total_overtime_1_hrs = 0
        total_overtime_2_hrs = 0
        for day in xrange(1, total_days_in_this_month + 1):
            today_sal = 0.0
            isMor = self.is_morning(day)
            sal_per_hour = base_sal_per_hour
            hours = self.get_working_hours(day)
            total_working_hours += hours
            #meal_fee = 0.0 # breakfirst_fee
            if isMor == False:
                #meal_fee += dinner_fee
                sal_per_hour += night_allowance_weight
                night_working_days += 1
            else:
                if hours > 0:
                    morning_working_days += 1
           
            rest_days = holidays[str(year)][int(month) - 1]
            today_hours = hours
            #base_sal = 0.0
            if hours > 8.0: 
                hours -= 8.0
                #base_sal += 8 * sal_per_hour
            else:
                #base_sal += hours * sal_per_hour
                hours = 0.0
            overtime_1_sal = 0.0
            if hours > 2:
                hours -= 2.0
                overtime_1_sal += 2 * sal_per_hour * 1.33
                total_overtime_1_hrs += 2
            else:
                overtime_1_sal += hours * sal_per_hour * 1.33
                total_overtime_1_hrs += hours
                hours = 0.0
            overtime_2_sal = 0.0
            if hours > 0.0:
                overtime_2_sal += hours * sal_per_hour * 1.66
                total_overtime_2_hrs += hours
            #today_sal += base_sal + overtime_1_sal + overtime_2_sal
            today_sal += overtime_1_sal + overtime_2_sal
            if self.get_working_hours(day) > 0.0:
                working_days_per_month += 1
            overtime_salary += today_sal
            today_str = '{}/{}/{}'.format(year, month, day)
            day_str = 'Day'
            if self.is_rest_day(today_str):
                day_str = '*Day'
                print("{:4}: {:2} [{:5} - {:5}], {:5.2f} hrs, {:9} + {:12} = {:12} ({})".format(
                            day_str,
                            day, 
                            self.on_work_time[day], 
                            self.off_work_time[day], 
                            today_hours,
                            overtime_1_sal, 
                            overtime_2_sal, 
                            today_sal,
                            overtime_salary))
                overtime_salary = 0
            else:
                print("{:4}: {:2} [{:5} - {:5}], {:5.2f} hrs, {:9} + {:12} = {:12}".format(
                            day_str,
                            day, 
                            self.on_work_time[day], 
                            self.off_work_time[day], 
                            today_hours,
                            overtime_1_sal, 
                            overtime_2_sal, 
                            today_sal))
        if working_days_per_month <= 0:
            return 0
        base_working_hrs = (total_days_in_this_month - rest_days) * 8
        extra_working_hrs = total_working_hours - base_working_hrs
        extra1 = extra_working_hrs - total_overtime_1_hrs - total_overtime_2_hrs
        print("Base hrs = {}, Rest days = {}, mor: {}, nig: {}, total: {} hrs, extra: {} + {} + {} = {} hrs".format(
                    base_working_hrs,
                    rest_days, 
                    morning_working_days, 
                    night_working_days,
                    total_working_hours,
                    extra1,
                    total_overtime_1_hrs,
                    total_overtime_2_hrs,
                    extra_working_hrs))
        print("Working days = {}".format(working_days_per_month))
        final = 0
        sal_per_month = base_sal_per_month
        agency_fee = self.agency_fee
        labor_insurance_fee = self.labor_insurance_fee
        accommodation_fee = self.accommodation_fee
        # for new hire, only calculate days
        if self.is_new_hire(year, month):
            not_avail_days = total_days_in_this_month - morning_working_days - night_working_days
            sal_per_month -= base_sal_per_day * not_avail_days
            agency_fee = 0
            labor_insurance_fee = 0
            accommodation_fee = 0
        if overtime_salary > 0.0:
            meal_fee = night_working_days * dinner_fee
            
            final = sal_per_month - agency_fee - labor_insurance_fee - accommodation_fee + meal_fee
            print("Salary: {} - {} - {} - {} + {} + {} = {}. Unpaid: {}".format(
                        sal_per_month, 
                        agency_fee, 
                        labor_insurance_fee, 
                        accommodation_fee, 
                        breakfirst_fee_per_month,
                        meal_fee,
                        final,
                        overtime_salary)) 

        return final
if __name__ == "__main__":
    m = employee(name='GG', factor=0.5, weight=30)
    print("Salary: {}".format(m.get_salary()))
