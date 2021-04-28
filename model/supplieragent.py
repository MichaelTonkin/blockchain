from controller.inventory import load_inventory
import json, requests
items_list = load_inventory()
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"


class SupplierAgent:

    def __init__(self, product, quantity, start_date, end_date, frequency):
        self.product = product
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency

    def process_request(self):

        response_data = {
            'company': 'placeholder',
            'stock': 0,
            'price': 0
        }
        print(self.product)
        print(items_list)
        #check that supplier has the requested goods in stock
        if self.product in items_list: #if the supplier has all or some of the requested item in stock
            response_data['accepted'] = True
            response_data['stock'] = self.quantity
            response_data['price'] = int(items_list[self.product][1][0]) * int(self.quantity)
            print("accepted request")

            return json.dumps(response_data)
        else:
            return json.dumps(response_data)


