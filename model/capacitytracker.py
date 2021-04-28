from datetime import date, datetime, timedelta
from collections import OrderedDict
import json


def generate_days(start, end):
    delta = end - start  # as timedelta
    days = []
    for i in range(delta.days + 1):
        day = start + timedelta(days=i)
        days.append(day)

    return days


def load_transports():

    with open('model/transports.json', 'r') as myfile:
        data = myfile.read()
    transports = {}
    try:
        transports = json.loads(data)
    except ValueError:
        print('No transports to load')
    return transports


def save_details_to_file(data):
    with open('model/daily_capacity.json', 'w') as outfile:
        json.dump(data, outfile)


def calculate_capacity():
    transports = load_transports()
    total_capacity = 0.0
    for key in transports:
        total_capacity += float(transports[key])

    return total_capacity


def dateslist_to_str(l):
    result = []
    for day in l:
        result.append(day.strftime("%d/%m/%Y"))
        print(day.strftime("%d/%m/%Y"))
    return result


def str_to_dateslist(s):
    result = []
    for day in s:
        result.append(date.strftime(day, "%d/%m/%Y"))
    return result


def generate_dates_file(new_capacity):
    """
    :param new_capacity: indicates a new transport which needs to be added. If this is 0, then it will be unused.
    :return:
    """
    # if file is empty: from today print each day for 6 months with fixed capacity
    days_list = generate_days(date.today(), date.today() + timedelta(days=182))
    total_capacity = calculate_capacity()
    capacity_list = []
    today_dat = date.today()
    today_str = date.today().strftime("%d/%m/%Y")
    str_stored_days = {}
    #import the file as stored_days

    try:
        with open('model/daily_capacity.json', 'r') as file:
            stored_days = json.loads(file.read())
    except:
        stored_days = {}

    if not stored_days or new_capacity >= 0:
        for i in range(0, len(days_list)):
            capacity_list.append(total_capacity)
        str_stored_days = (OrderedDict(zip(dateslist_to_str(days_list), capacity_list))) # a string version of the stored_days list
                                                                                # which can be used in iteration
        print(str_stored_days)
    #while day != current day: delete day and add new day to end
    i = 0

    #delete days up to the current date and append a new day to the end for each iteration
    for day in str_stored_days:
        i += 1

        if day == today_str:
            break
        str_stored_days.pop(day)
        str_stored_days[(today_dat + timedelta(days=182 + i)).strftime("%d/%m/%Y")] = total_capacity


    if str_stored_days == {}:
        print("CapacityTracker: Nothing new to add.")
    else:
        save_details_to_file(str_stored_days)
