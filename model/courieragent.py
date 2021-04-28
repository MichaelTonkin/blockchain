from model.capacitytracker import generate_dates_file
from collections import OrderedDict
import sys, json, requests
from datetime import date
from datetime import datetime as dt


def get_company_details():
    with open('model/peerdata.json', 'r') as file:
        data = json.loads(file.read())
    return data


def get_ia_node():
    with open('model/ia_address.json', 'r') as file:
            data = str(file.read())
    return data[1 : len(data)-1]


class CourierAgent:

    def __init__(self, quantity, start_date, end_date, frequency):
        self.quantity = float(quantity)
        self.start_date = dt.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%y')
        self.end_date = dt.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%y')
        self.frequency = frequency

    def process_request(self):

        response_data = {
            'company': get_company_details()["name"],
            'dates': []
        }

        with open('model/daily_capacity.json', 'r') as file:
            transport_calendar = OrderedDict(json.loads(file.read()))

        if self.frequency == "daily":
            for day in transport_calendar:
                if day >= self.end_date:
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
                cont_quantity = self.quantity
                index += 7
                if week >= self.end_date:
                    break
                if week >= self.start_date:
                    for cap in range(index - 7, index, 1): #add the capacity for all the days in this week
                        weekly_capacity += transport_calendar[list_calendar[cap]]
                        if weekly_capacity < self.quantity:
                            print("not enough capacity: " + str(weekly_capacity) + " required: " + str(self.quantity))
                            break
                        else:
                            response_data["dates"].append(list_calendar[cap])
                            print("resp = " + str(response_data["dates"]))
                        transport_calendar[list_calendar[cap]] -= cont_quantity
                        cont_quantity -= cont_quantity

                        if transport_calendar[list_calendar[cap]] < 0:
                            cont_quantity += transport_calendar[list_calendar[cap]]
                            transport_calendar[list_calendar[cap]] -= cont_quantity

                        if cont_quantity == 0:
                            break

        with open('model/daily_capacity.json', 'w') as outfile:
            json.dump(transport_calendar, outfile)

        print(response_data)
        #send data to blockchain quantity, start_date, end_date, frequency
        if response_data['dates']:
            requests.post(url="{}/new_transactions".format(get_ia_node()),
                          json={
                              "company": response_data["company"],
                              "volume": self.quantity,
                              "req_status": 'Request',
                              "item_type": 'Delivery',
                              "starting_date": self.start_date,
                              "ending_date": self.end_date,
                              "frequency": self.frequency,
                          },
                          headers={'Content-type': 'application/json'})

        return json.dumps(response_data)