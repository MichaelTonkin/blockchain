from controller.inventory import load_inventory
import sys, json
items_list = load_inventory()

class CourierAgent:

    def __init__(self, product, quantity, start_date, end_date, frequency):
        self.product = product
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency

    def process_request(self):

        response_data = {
            'accepted': False,
            'dates': []
        }

        transport_calendar = {} # to be loaded from file

        #If frequency is daily
        #For each day between start and finish dates: check that we have the capacity to perform the transport service
        #IF we have the capacity: reduce capacity for that day in transport_calendar
        #ELSE go to the next date in range
        #The supplier agent will need to decide what to do if all dates cannot be accommodated for.

        #If frequency is weekly
        #For each week in range start to end
        #Add the value of carrying capacity each day to running total.
        #If we have enough capacity for that week:
        #starting from earliest date subtract capacity from the day and running total, adding each day to the list
        #until we have met the demand.



        return json.dumps(response_data)




