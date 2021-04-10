from model.capacitytracker import generate_dates_file
import sys, json
from datetime import date, timedelta


class CourierAgent:

    def __init__(self, quantity, start_date, end_date, frequency):
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency

    def process_request(self):

        response_data = {
            'company': "placeholder",
            'dates': []
        }

        with open('daily_capacity.json', 'r') as file:
            transport_calendar = json.loads(file.read())

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
            weekly_capacity = 0
            for week in range(0, len(transport_calendar), 7):
                if week >= self.end_date:
                    break
                if week >= self.start_date:
                    for cap in range(week, len(transport_calendar), 7):
                        weekly_capacity += transport_calendar.values()[cap]
                        #you can edit the json file while going through this, then just discard it if unused
                        if weekly_capacity < self.quantity:
                            break



        with open('daily_capacity.json', 'w') as outfile:
            json.dump(transport_calendar, outfile)



        print(response_data)
        #If frequency is weekly
        #For each week in range start to end
        #Add the value of carrying capacity each day to running total.
        #If we have enough capacity for that week:
        #starting from earliest date subtract capacity from the day and running total, adding each day to the list
        #until we have met the demand.

        return json.dumps(response_data)






