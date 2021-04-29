from flask import request, redirect,render_template
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json, socket
from view import app
from model.peer import Peer

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
msg = ""

@app.route('/details')
def get_details_page():
    global msg
    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('details.html')
    return template.render(node_address=CONNECTED_NODE_ADDRESS, msg=msg)


def save_details_to_file(peer, intelligent_agent):
    with open('model/peerdata.json', 'w') as outfile:
        json.dump(peer.to_json(), outfile)
    with open('model/ia_address.json', 'w') as outfile:
        json.dump(intelligent_agent, outfile)


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
    global msg
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
         products=load_inventory(),
         ip="http://"+address,
         physical_address=request.form["physical_address"])

    ia = request.form["information_node"]

    save_details_to_file(node, ia)

    registration_address = "{}/register_node".format(ia)

    requests.post(registration_address,
                  json=company_details,
                  headers={'Content-type': 'application/json'})
    msg += "Success"
    # Return to the homepage
    return redirect('/details')