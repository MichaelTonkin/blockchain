from flask import request, redirect,render_template
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json, socket
from view import app
from model.peer import Peer
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"


@app.route('/details')
def get_details_page():

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('details.html')
    return template.render(node_address=CONNECTED_NODE_ADDRESS)


def save_details_to_file(peer):
    with open('model/peerdata.json', 'w') as outfile:
        json.dump(peer.to_json(), outfile)


def open_details_file():
    with open('model/peerdata.json', 'r') as myfile:
        data = myfile.read()
    return data


def load_inventory():
    data = open_details_file()
    try:
        node = json.loads(data)
        inventory = node['products']
    except:
        inventory = {}
    return inventory


@app.route('/submit_details', methods=['POST'])
def submit_details():
    """
    Send the company details to the information agent on this network
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    address = s.getsockname()[0]
    s.close()

    company_details = {
        'name': request.form["name"],
        'company_type': request.form["company_type"],
        'physical_address': request.form["physical_address"],
        'node_address': "http://"+address,
        'information_node': request.form["information_node"],
        'products': list(load_inventory().keys())
    }

    node = Peer(name=request.form["name"],
         company_type=request.form["company_type"],
         products={},
         ip="http://"+address,
         physical_address=request.form["physical_address"])

    save_details_to_file(node)

    information_agent_ip = request.form["information_node"]

    registration_address = "{}/register_node".format(information_agent_ip)

    requests.post(registration_address,
                  json=company_details,
                  headers={'Content-type': 'application/json'})

    # Return to the homepage
    return redirect('/details')