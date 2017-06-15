#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
    
def get_hr(t):
    return int(t.split(':')[0])
def get_min(t):
    return int(t.split(':')[1])

def get_datetime(time_str):
    if time_str == None or len(time_str) == 0:
        return None
    datetime_format = '%H:%M'
    return datetime.strptime(time_str, datetime_format)

def get_datetime_date(time_str):
    if time_str == None or len(time_str) == 0:
        return None
    datetime_format = '%Y/%m/%d'
    return datetime.strptime(time_str, datetime_format)
