import json, requests
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

def open_details_file():
    with open('model/peerdata.json', 'r') as file:
        data = file.read()
    return data

def load_inventory():
    data = open_details_file()
    inventory = ""
    try:
        node = json.loads(data)
        inventory = node['products']
    except:
        print("Nothing to load in inventory.")
    return inventory


def get_company_details():
    with open('model/peerdata.json', 'r') as file:
        data = json.loads(file.read())
    return data


def get_ia_node():
    with open('model/ia_address.json', 'r') as file:
            data = str(file.read())
    return data[1 : len(data)-1]



class SupplierAgent:

    def __init__(self, product, quantity, start_date, end_date, frequency):
        self.product = product
        self.quantity = quantity
        self.start_date = start_date
        self.end_date = end_date
        self.frequency = frequency
        self.items_list = load_inventory()

    def process_request(self):

        response_data = {
            'company': get_company_details()["name"],
            'stock': 0,
            'price': 0
        }
        print(self.product)
        print(self.items_list)
        #check that supplier has the requested goods in stock
        if self.product in self.items_list: #if the supplier has all or some of the requested item in stock
            if int(self.items_list[self.product][0][0]) >= int(self.quantity):
                response_data['accepted'] = True
                response_data['stock'] = self.quantity
                response_data['price'] = int(self.items_list[self.product][1][0]) * int(self.quantity)
                print("accepted request")
                requests.post(url="{}/new_transactions".format(get_ia_node()),
                              json={
                                  "company": response_data["company"],
                                  "volume": self.quantity,
                                  "req_status": 'Offer',
                                  "item_type": self.product,
                                  "starting_date": self.start_date,
                                  "ending_date": self.end_date,
                                  "frequency": self.frequency,
                              },
                              headers={'Content-type': 'application/json'})
        return json.dumps(response_data)



