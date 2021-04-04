from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import json
from view import app
from model.capacitytracker import generate_dates_file

transport_list = []


@app.route('/transports')
def load_transports_page():
    global transport_list

    transport_list = [load_transports()]

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('transports.html')

    return template.render(transport_list=transport_list)


def save_details_to_file(data):
    with open('model/transports.json', 'w') as outfile:
        json.dump(data, outfile)


def open_details_file():
    with open('model/transports.json', 'r') as myfile:
        data = myfile.read()
    return data


def load_transports():
    transports = {}
    try:
        data = open_details_file()
        transports = json.loads(data)
    except ValueError:
        print('No transports to load')
    return transports


@app.route('/add_transport', methods=['POST'])
def add_transport():
    """
    Adds a transport and corresponding transport capacity to file
    """
    reg = request.form['reg']
    capacity = request.form['capacity']
    data = load_transports()
    data[reg] = float(capacity)
    save_details_to_file(data)
    generate_dates_file(capacity)
    return redirect('/transports')


@app.route('/remove_transport', methods=['POST'])
def remove_transport():
    """Allows the user to click a transport to delete it from file"""
    transports = load_transports()

    item = request.form['key_value']

    del transports[item]

    save_details_to_file(transports)
    generate_dates_file(1)

    del item

    return redirect('/transports')