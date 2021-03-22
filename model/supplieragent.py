from controller.inventory import load_inventory, save_details_to_file

items_list = load_inventory()

class SupplierAgent:

    def __init__(self, product, quantity, due_date):
        self.product = product
        self.quantity = quantity
        self.due_date = due_date

    def process_request(self):

        #check that supplier has the requested goods in stock
        if self.product in items_list:
            if items_list[self.product][0] >= self.quantity:
                return int(items_list[self.product][1][0]) * self.quantity # if we have the item in stock, return price for quantity
            else:
                return "Item not in stock"
        elif items_list[self.product][2] * self.get_date_difference() < self.due_date: # if enough product can be produced before due date
            return self.due_date
        else:
            return "Request rejected."

    def get_date_difference(self):
        pass

