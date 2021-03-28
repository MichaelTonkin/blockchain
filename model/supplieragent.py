from controller.inventory import load_inventory
import sys, json
items_list = load_inventory()

class SupplierAgent:

    def __init__(self, product, quantity, start_date, end_date, frequency):
        self.product = product
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency

    def process_request(self):

        response_data = {
            'accepted': False,
            'stock': 0,
            'price': 0
        }
        print(items_list)
        #check that supplier has the requested goods in stock
        if self.product in items_list: #if the supplier has all or some of the requested item in stock
            response_data['accepted'] = True
            response_data['stock'] = self.quantity
            response_data['price'] = int(items_list[self.product][1][0]) * self.quantity
            print("accepted request")
            return json.dumps(response_data)
        else:
            return json.dumps(response_data)



