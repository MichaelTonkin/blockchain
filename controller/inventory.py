from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import json, requests
from model.peer import Peer
from view import app


items_list = []


@app.route('/inventory')
def load_inventory_page():
    global items_list

    items_list = []

    items_list.append(load_inventory())

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('inventory.html')

    return template.render(items_list=items_list)


def save_details_to_file(node):
    with open('model/peerdata.json', 'w') as outfile:
        json.dump(node, outfile)


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


def announce_new_item():
    with open('model/ia_address.json', 'r') as file:
        url = file.readline()
    with open('model/peerdata.json', 'r') as file:
        company_details = json.load(file)

    registration_address = "{}/register_node".format(url[1:len(url)-1])

    requests.post(registration_address,
                  json=company_details,
                  headers={'Content-type': 'application/json'})


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
    price = request.form['price']
    producable = request.form['producable'] # the amount of this product which can be produced each day

    if item in inventory:
        inventory[item][0] = [int(inventory[item][0][0]) + int(amount)]
        inventory[item][1] = [int(price)]
        inventory[item][2] = [float(producable)]
    else:
        inventory[item] = []
        inventory[item].append([int(amount)])
        inventory[item].append([int(price)])
        inventory[item].append([float(producable)])

    node['products'] = inventory

    save_details_to_file(node)
    announce_new_item()
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