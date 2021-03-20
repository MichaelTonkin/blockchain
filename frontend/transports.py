from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import json
from frontend import app


transports_list = []


@app.route('/transports')
def load_inventory_page():
    global transports_list

    transports_list = []

    transports_list.append(load_inventory())

    env = Environment(
        loader=PackageLoader('frontend', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('transports.html')

    return template.render(transports_list=transports_list)


def save_details_to_file(node):
    with open('backend/peerdata.json', 'w') as outfile:
        json.dump(node, outfile)


def open_details_file():
    with open('backend/peerdata.json', 'r') as myfile:
        data = myfile.read()
    return data


def load_inventory():
    data = open_details_file()

    node = json.loads(data)
    inventory = node['products']
    return inventory


@app.route('/add_to_inventory', methods=['POST'])
def add_to_inventory():
    """
    Adds an item to the company inventory
    """
    data = open_details_file()

    node = json.loads(data)
    inventory = load_inventory()

    item = request.form['item']
    amount = request.form['amount']

    if item in inventory:
        inventory[item] = int(inventory[item]) + int(amount)
    else:
        inventory[item] = int(amount)

    node['products'] = inventory

    save_details_to_file(node)

    return redirect('/inventory')


@app.route('/remove_from_inventory', methods=['POST'])
def remove_from_inventory():
    """Removes an item from the company inventory"""

    data = open_details_file()

    node = json.loads(data)
    inventory = load_inventory()

    item = request.form['key_value']
    print(item)
    if item in inventory:
        inventory.pop(item)

    node['products'] = inventory

    save_details_to_file(node)

    del item

    return redirect('/inventory')