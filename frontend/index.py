from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json
from frontend import app
from util import *

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []
invoices = []
address = load_address_from_file()

@app.route('/')
def index_page():
    """Provides data for the index.html page on the front-end."""
    fetch_posts()
    env = Environment(
        loader=PackageLoader('frontend', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')

    return template.render(posts=posts, invoices=invoices, node_address=CONNECTED_NODE_ADDRESS)


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data, and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    decrypt_url = "{}/decrypt".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)

    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)

        #iterate through each block and their transactions
        for block in chain["chain"]:
            content.append(block)
            for transaction in block["transactions"]:
                customer_pos = transaction.find("Customer") #get the customer id from transaction
                if customer_pos is not -1:
                    customer = transaction[customer_pos + 9:]
                    customer = customer[0:len(customer)-1]
                    if customer == address:
                        encrypted = transaction.split(" ")
                        decrypt_response = requests.post(decrypt_url, data=encrypted[1][1:])
                        invoices.append(decrypt_response.content)

        global posts
        posts = content


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application
    """
    manufacturer_id = request.form["manufacturer_id"]
    initial_id = request.form["initial_id"]
    weight = request.form["weight"]
    customer_id = request.form["customer_id"]

    product_object = {
        'manufacturer_id': manufacturer_id,
        'initial_id': initial_id,
        'weight': weight,
        'customer_id': customer_id,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transactions".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=product_object,
                  headers={'Content-type': 'application/json'})

    # Return to the homepage
    return redirect('/')


