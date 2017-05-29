#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, traceback
from datetime import datetime, timedelta
from var import *
import math
import calendar
from date_util import *
#from peewee import *
# Use deferring initialization
#db = SqliteDatabase(None)

datetime_format = '%H:%M'

class employee:
    def __init__(self, name ='TEST', hire_date = '2017/01/01', factor = 0.3333333, weight = 0.0, agency_fee = 1500, labor_fee = 399, insurance_fee = 296, accommodation_fee = 2500, unpaid_last = 0):
        self.name = name
        self.hire_date = hire_date
        self.factor = factor
        self.weight = weight
        self.on_work_time = 32 * [None] # preallocate time 
        self.off_work_time = 32 * [None] # preallocate time
        self.agency_fee = agency_fee
        self.labor_fee = labor_fee
        self.insurance_fee = insurance_fee
        self.accommodation_fee = accommodation_fee
        self.unpaid_last = unpaid_last
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
        t1 = get_datetime('00:00')
        t2 = get_datetime(time)
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
                if get_hr(on_time) <= 8.0:
                    on_time = '08:00' 
                    off_time = '08:00' 
                continue

            # beautify on_time, if on_time <= 8:00, set on_time = '8:00'
            if get_hr(on_time) <= 8.0:
                on_time = '08:00'
            

            on_time_hr = get_hr(on_time)
            off_time_hr = get_hr(off_time)

            min_diff = (get_datetime(off_time) - get_datetime(on_time)).total_seconds() / 60.0
            if abs(min_diff) < 15:
                self.on_work_time[day] = on_time
                self.off_work_time[day] = on_time
                continue
            on_time_min = get_min(on_time)
            off_time_min = get_min(off_time)

            on_time_round_min = self.time_rounding(on_time, True)
            off_time_round_min = self.time_rounding(off_time, False)


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
            new_off_time_str = '{}:{}'.format(get_hr(off_time), off_time_min_str)

            self.on_work_time[day] = new_on_time_str
            self.off_work_time[day] = new_off_time_str
        
    def set_working_data(self, day, on_time, off_time): # day = 1 to 31
        self.on_work_time[day] = on_time
        self.off_work_time[day] = off_time
    def is_morning_time(self, time):
        if get_datetime('17:30') <= time <= get_datetime('23:59'):  
            return False
        return True
        
    def is_morning(self, day): # day = 1 to 31
        on_work_day_str = self.on_work_time[day]
        if on_work_day_str == None or len(on_work_day_str) == 0:
            return None
        t1 = get_datetime(self.on_work_time[day])
        if t1 == None:
            return None
        return self.is_morning_time(t1)

    # input 2017/04/20 --> return 4
    def get_month(self, datetime_str):
        int(datetime_str.split('/')[1])
    # input 2017/04/20 --> return 20
    def get_day(self, datetime_str):
        int(datetime_str.split('/')[2])

    def is_rest_day(self, time_str):
        t1 = get_datetime_date(time_str)
        t2 = get_datetime_date('2017/05/14')
        day_diff = abs((t1 - t2).total_seconds() / 60.0 / 60.0 / 24.0)
        if day_diff % 14 == 0:
            return True
        return False

    def get_rest_hours(self, day): 
        flag = 0
        if self.on_work_time[day] == None:
            return 0.0
        if self.off_work_time[day] == None:
            return 0.0

        t1 = get_datetime(self.on_work_time[day])        
        t2 = get_datetime(self.off_work_time[day])
        if t1 == None or t2 == None:
            return 0.0
        if t1 < t2:
            if t1 <= get_datetime('05:15') <= t2:  # through breakfirst
                flag += 1
            if t1 <= get_datetime('12:15') <= t2:  # through lunch
                flag += 2
            if t1 <= get_datetime('17:15') <= t2:  # through dinner
                flag += 4
        else:
            if t1 >= get_datetime('05:15') >= t2:  # through breakfirst
                flag += 1
            if t1 >= get_datetime('12:15') >= t2:  # through lunch
                flag += 2
            if t1 >= get_datetime('17:15') >= t2:  # through dinner
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
        t1 = get_datetime(self.on_work_time[day])
        t2 = get_datetime(self.off_work_time[day]) - timedelta(hours=rest_hours)
        if t1 == None or t2 == None:
            return 0.0
        if t1 <= t2:
            return (t2 - t1).total_seconds() / 3600.0
        else:
            t3 = get_datetime('23:59') - t1;
            t4 = t2 - get_datetime('00:00')
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
    
    def get_base_rest_days(self, year, month, day):
        date_str = '{}/{}/{}'.format(year, month, day)
        current_date = get_datetime_date(date_str)
        current_day = current_date.day
        #print('current day: {}'.format(current_day))
        previous_checkpoint = current_date - timedelta(days=14)
        previous_day = previous_checkpoint.day
        #print('previous_day: {}'.format(previous_day))
        month = current_date.month
        lst = hol[str(month)]
        #print("lst len: {}".format(len(lst)))
        #'4': [1, 2, 3, 4, 8, 9, 15, 16, 22, 23, 29, 30],
        rest_days = []
        if current_day < previous_day:
            previous_day = 0
        for e in lst:
            if e > previous_day and e <= current_day:
                rest_days.append(e)
        #print("len of rest_days: {}".format(len(rest_days)))
        return len(rest_days)
    def get_extra_pay_day_list(self, year, month): # every 14 days
        lst = []
        total_days_in_this_month = calendar.monthrange(int(year), int(month))[1]
        for day in xrange(1, total_days_in_this_month + 1): 
            today_str = '{}/{}/{}'.format(year, month, day)
            if self.is_rest_day(today_str):
                lst.append(day)
        return lst
    def get_tax(self, year, month):
        # working days <= 183
        # 21009 * 6%
        t = '{}/{}/28'.format(year, month)
        t1 = get_datetime_date(self.hire_date)
        t2 = get_datetime_date(t)
        day_diff = abs((t2 - t1).total_seconds() / 60.0 / 60.0 / 24.0)
        if day_diff < 183:
            return int(base_sal_per_month * 0.06) # 6%
        return 0.0

    def get_salary_per_day(self, day):
        today_sal = 0.0
        sal_per_hour = base_sal_per_hour
        base_sal = 0.0 
        today_hours = self.get_working_hours(day)
        is_night = False 
        is_mor = self.is_morning(day)
        if is_mor == False:
            sal_per_hour += night_allowance_weight
            if today_hours > 0.0:
                is_night = True
        hours = today_hours
        base_hours = 0.0
        if hours >= 8.0: 
            hours -= 8.0
            base_hours = 8.0
            if is_night == True:
                base_sal += 8 * night_allowance_weight 
        else:
            base_hours = hours
            hours = 0.0
        overtime1_sal = 0.0
        overtime1_hrs = 0
        if hours >= 2.0:
            hours -= 2.0
            overtime1_hrs += 2
            overtime1_sal += 2 * sal_per_hour * weight133
        else:
            overtime1_sal += hours * sal_per_hour * weight133
            overtime1_hrs += hours
            hours = 0.0
        overtime2_sal = 0.0
        overtime2_hrs = 0
        if hours > 0.0:
            overtime2_sal += hours * sal_per_hour * weight166 
            overtime2_hrs = hours
        today_sal += base_sal + overtime1_sal + overtime2_sal
        return {'today_sal': today_sal,
            'is_mor': is_mor,
            'is_night': is_night,
            'today_hours': today_hours,
            'base_hours': base_hours,
            'base_sal': base_sal,
            'overtime1_hrs': overtime1_hrs,
            'overtime2_hrs': overtime2_hrs,
            'overtime1_sal': overtime1_sal,
            'overtime2_sal': overtime2_sal}
    def get_two_week_sal(self, stage_num, left, right, extra_pay_day_list, year, month):
        total_working_hours = 0     # 總工作時數
        base_working_days = 0       # 基本工作時數 8hr
        total_overtime1_hrs = 0     # 前兩小時加班
        total_overtime2_hrs = 0     # 超過兩小時加班
        overtime_salary = 0         # 總加班費
        morning_working_days = 0    # 早班天數 
        night_working_days = 0      # 晚班天數

        total_mor_hours = 0
        total_nig_hours = 0         # 晚班總時數 (須給付夜津)
        
        off_day_list = [] # 公休日
        for e in extra_pay_day_list:
            off_day_list.append(self.get_base_rest_days(year, month, e))
        #print("rest day list for every two weeks: {}".format(off_day_list))


        for day in xrange(left, right+1):
            dic = self.get_salary_per_day(day)
            
            total_working_hours += dic['today_hours']
            total_overtime1_hrs += dic['overtime1_hrs']
            total_overtime2_hrs += dic['overtime2_hrs']
            if dic['is_mor'] == True:
                morning_working_days += 1
                total_mor_hours += dic['today_hours']
            if dic['is_night'] == True:
                night_working_days += 1
                total_nig_hours += dic['today_hours']
        if stage_num == 1:
            base_working_days = (extra_pay_day_list[0] - off_day_list[0])
        else:
            base_working_days = (extra_pay_day_list[stage_num-1] - extra_pay_day_list[stage_num-2] - off_day_list[stage_num-1])
        base_working_hrs = base_working_days * 8
        overtime_hrs = total_working_hours - base_working_hrs
        
        actual_working_days = morning_working_days + night_working_days 
        total_overtime_hrs = total_working_hours - total_overtime1_hrs - total_overtime2_hrs - base_working_hrs
        off_day = actual_working_days - base_working_days
        minus = 0
        if off_day < 0:
            minus = off_day * base_sal_per_day
        overtime_salary = (total_overtime_hrs + weight133 * total_overtime1_hrs + weight166 * total_overtime2_hrs) * base_sal_per_hour - minus + total_nig_hours * night_allowance_weight
        print("Stage {}: working hrs: {}, base_working_days: {}, mor: {}, nig: {}, overtime: {}, overtime1: {}, overtime2: {}, off day: {}, overtime: {}, night: {}".format(
                    stage_num,
                    total_working_hours,
                    base_working_days, 
                    morning_working_days, 
                    night_working_days, 
                    total_overtime_hrs, 
                    total_overtime1_hrs, 
                    total_overtime2_hrs, 
                    off_day, 
                    overtime_salary,
                    total_nig_hours * night_allowance_weight))
    def get_salary(self, year, month):
        overtime_salary = 0.0
        working_days_per_month = 0
        morning_working_days = 0
        night_working_days = 0
        total_working_hours = 0
        total_base_working_hours = 0
        total_days_in_this_month = calendar.monthrange(int(year), int(month))[1]
        total_overtime1_hrs = 0
        total_overtime2_hrs = 0

        dict_list = []
        day_list = []
        sal_list = []
        extra_pay_list = []
        rest_days = holidays[str(year)][int(month) - 1]
        
        extra_pay_day_list = self.get_extra_pay_day_list(year, month)
        print("pay day list: {}".format(extra_pay_day_list))
        
        self.get_two_week_sal(1, 1, extra_pay_day_list[0] + 1, extra_pay_day_list, year, month)
        self.get_two_week_sal(2, extra_pay_day_list[0] + 1, extra_pay_day_list[1], extra_pay_day_list, year, month)
        if len(extra_pay_day_list) > 2:
            self.get_two_week_sal(3, extra_pay_day_list[1] + 1, extra_pay_day_list[2], extra_pay_day_list, year, month)
        
        total_working_hours = 0
        total_base_working_hours = 0
        total_overtime1_hrs = 0
        total_overtime2_hrs = 0
        overtime_salary = 0 

        for day in xrange(1, total_days_in_this_month + 1):
            dic = self.get_salary_per_day(day)
            total_working_hours += dic['today_hours']
            total_base_working_hours += dic['base_hours'] 
            total_overtime1_hrs += dic['overtime1_hrs']
            total_overtime2_hrs += dic['overtime2_hrs']
            overtime_salary += dic['today_sal']

            if dic['is_mor'] == True:
                morning_working_days += 1
            if dic['is_night'] == True:
                night_working_days += 1

            if dic['today_hours'] > 0.0:
                working_days_per_month += 1
            
            today_str = '{}/{}/{}'.format(year, month, day)
            day_str = 'Day'
            rest_day_marker = ''



            if self.is_rest_day(today_str): # a check point
                day_str = '*Day'
                rest_day_marker = '*'
                base_rest_days = self.get_base_rest_days(year, month, day)
                print("{:4}: {:2} [{:5} - {:5}], {:5.2f} hrs, {:9} + {:12} = {:12} ({})".format(
                            day_str,
                            day, 
                            self.on_work_time[day], 
                            self.off_work_time[day], 
                            dic['today_hours'],
                            dic['overtime1_sal'], 
                            dic['overtime2_sal'], 
                            dic['today_sal'],
                            overtime_salary))
                extra_pay_list.append(overtime_salary)
                overtime_salary = 0
            else:
                print("{:4}: {:2} [{:5} - {:5}], {:5.2f} hrs, {:7} + {:9} + {:12} = {:12}".format(
                            day_str,
                            day, 
                            self.on_work_time[day], 
                            self.off_work_time[day], 
                            dic['today_hours'],
                            dic['base_sal'],
                            dic['overtime1_sal'], 
                            dic['overtime2_sal'], 
                            dic['today_sal']))
            day_list.append({'day': '{:1}{:2} [{:5} - {:5}] {:10.2f} hrs'.format(rest_day_marker, day, self.on_work_time[day], self.off_work_time[day], dic['today_hours']), 
                    'base': float(dic['base_hours']), 
                    'base133': float(dic['overtime1_hrs']), 
                    'base166': float(dic['overtime2_hrs'])})
            sal_list.append({'day': '{:1}{:2} [{:5} - {:5}]'.format(rest_day_marker, day, self.on_work_time[day], self.off_work_time[day]), 
                    'base': dic['base_sal'], 
                    'base133': dic['overtime1_sal'], 
                    'base166': dic['overtime2_sal']})
        if working_days_per_month <= 0:
            return 0
        base_working_days = (total_days_in_this_month - rest_days)
        base_working_hrs = base_working_days * 8
        extra_working_hrs = total_working_hours - base_working_hrs
        extra1 = extra_working_hrs - total_overtime1_hrs - total_overtime2_hrs

        print("Base hrs = {}, Rest days = {}, mor: {}, nig: {}, total: {} hrs, extra: {} + {} + {} = {} hrs".format(
                    base_working_hrs,
                    rest_days, 
                    morning_working_days, 
                    night_working_days,
                    total_working_hours,
                    extra1,
                    total_overtime1_hrs,
                    total_overtime2_hrs,
                    extra_working_hrs))
        print("Working days = {}".format(working_days_per_month))
        final_sal = 0
        sal_per_month = base_sal_per_month
        agency_fee = self.agency_fee
        labor_fee = self.labor_fee
        insurance_fee = self.insurance_fee
        accommodation_fee = self.accommodation_fee
        breakfirst_fee = breakfirst_fee_per_month 
        extra_bonus = 0.0
        # for new hire, only calculate days, agency, labor_insurance, and accommodation are free
        if self.is_new_hire(year, month):
            not_avail_days = total_days_in_this_month - morning_working_days - night_working_days
            sal_per_month -= base_sal_per_day * not_avail_days
            breakfirst_fee -= breakfirst_fee_per_day * not_avail_days
            ratio = (morning_working_days + night_working_days) / float(total_days_in_this_month)
            agency_fee = int(self.agency_fee * ratio)
            labor_fee = labor_fee * ratio
            accommodation_fee = 0
        meal_fee = 0.0
        if overtime_salary >= 0.0:
            meal_fee = night_working_days * dinner_fee
            if self.weight > 0:
                meal_fee = dinner_fee * self.weight # special rule for special employee
            extra_bonus = total_working_hours * self.factor * self.weight
            tax = self.get_tax(year, month)
            final_sal = sal_per_month - agency_fee - labor_fee -insurance_fee - accommodation_fee + meal_fee + breakfirst_fee + extra_bonus - tax
            print("Salary: {} - {} - {} - {} - {} + {} + {} + {} - {} = {}. Unpaid: {}".format(
                        sal_per_month, 
                        agency_fee, 
                        labor_fee, 
                        insurance_fee, 
                        accommodation_fee, 
                        breakfirst_fee,
                        meal_fee,
                        extra_bonus,
                        tax,
                        final_sal,
                        overtime_salary)) 
        dict_list = {'name': self.name, 
                'day': day_list,
                'sal': sal_list,
                'mor': morning_working_days,
                'nig': night_working_days,
                'total_hrs': total_working_hours,
                'total_base_hrs': total_base_working_hours,
                'extra_hrs': extra1,
                'total_overtime_1_hrs': total_overtime1_hrs,
                'total_overtime_2_hrs': total_overtime2_hrs,
                'base_working_days': base_working_days,
                'extra_working_hrs': extra_working_hrs,
                'sal_per_month': sal_per_month,
                'agency_fee': -agency_fee,
                'labor_fee': -labor_fee,
                'insurance_fee': -insurance_fee,
                'accommodation_fee': -accommodation_fee,
                'breakfirst_fee_per_month': breakfirst_fee,
                'meal_fee': meal_fee,
                'extra_bonus': extra_bonus,
                'rest_days': rest_days,
                'final_sal': final_sal,
                'unpiad_last': self.unpaid_last,
                'tax': -tax, 
                'extra_pay_list': extra_pay_list,
                'unpiad': overtime_salary}

        return dict_list
if __name__ == "__main__":
    m = employee(name='GG', factor=0.5, weight=30)
