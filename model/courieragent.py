from model.capacitytracker import generate_dates_file
from collections import OrderedDict
import sys, json
from datetime import date, timedelta


class CourierAgent:

    def __init__(self, quantity, start_date, end_date, frequency):
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency

    def process_request(self):

        cont_quantity = self.quantity

        response_data = {
            'company': "placeholder",
            'dates': ["test"]
        }

        with open('model/daily_capacity.json', 'r') as file:
            print(str(file.read()))
            transport_calendar = OrderedDict(file.read())

        today_str = date.today().strftime("%d/%m/%Y")
        #If frequency is daily
        #For each day between start and finish dates: check that we have the capacity to perform the transport service
        #IF we have the capacity: reduce capacity for that day in transport_calendar
        #ELSE go to the next date in range
        #The supplier agent will need to decide what to do if all dates cannot be accommodated for.
        if self.frequency == "daily":
            for day in transport_calendar:
                if day == self.end_date:
                    break
                if day >= self.start_date:
                    if transport_calendar[day] >= float(self.quantity):
                        transport_calendar[day] -= float(self.quantity)
                        response_data["dates"].append(day)
        elif self.frequency == "weekly":
            index = 0
            weekly_capacity = 0
            list_calendar = list(transport_calendar.keys())
            for week in list_calendar[::7]: #iterate through each week
                index += 7
                if week >= self.end_date:
                    print(week)
                    print(self.end_date)
                    break
                if week >= self.start_date:
                    for cap in range(index - 7, index, 1): #add the capacity for all the days in this week
                        weekly_capacity += transport_calendar[list_calendar[cap]]
                        print("wc" + str(weekly_capacity))
                        if weekly_capacity < self.quantity:
                            break
                        else:
                            response_data["dates"].append(transport_calendar[list_calendar[cap]])
                        transport_calendar[list_calendar[cap]] -= cont_quantity
                        cont_quantity -= cont_quantity

                        print("tc " + str(transport_calendar[list_calendar[cap]]))

                        if transport_calendar[cap] < 0:
                            cont_quantity += transport_calendar[list_calendar[cap]]
                            transport_calendar[list_calendar[cap]] -= cont_quantity

                        if cont_quantity == 0:
                            break
                    if cont_quantity == 0:
                        break
                if cont_quantity == 0:
                    break

        with open('daily_capacity.json', 'w') as outfile:
            json.dump(transport_calendar, outfile)

        print(response_data)

        return json.dumps(response_data)






