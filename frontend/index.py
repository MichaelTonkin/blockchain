from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json
from frontend import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []
invoice_posts = []
address = None

@app.route('/')
def index_page():
    """Provides data for the index.html page on the front-end."""
    fetch_posts()
    env = Environment(
        loader=PackageLoader('frontend', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')

    return template.render(posts=posts, invoices=invoice_posts, node_address=CONNECTED_NODE_ADDRESS)


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
        invoices = []
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
                        decrypt_response = [] #holds segments of the invoice which need to be decrypted.
                        for i in range(1, 9, 2):
                            decrypt_response.append(requests.post(decrypt_url, data=encrypted[i][1:]))
                        #construct decrypted transaction
                        inv = {"Date: ": decrypt_response[0].content, "Manufacturer Product ID: ": decrypt_response[1].content,
                               "Weight (KG): ": decrypt_response[2].content, "Initial Product ID: ": decrypt_response[3].content}
                        invoices.append(inv)

        global posts
        global invoice_posts
        invoice_posts = invoices
        posts = content


@app.route('/set_address', methods=['POST'])
def get_address_from_user():
    global address
    address = request.form["address"]

    return redirect('/')


@app.route('/submit_public_key', methods=['POST'])
def set_public_key():

    key = request.form["key"]

    forward_address = "{}/set_public_key".format(CONNECTED_NODE_ADDRESS)

    requests.post(forward_address,
                  json=key,
                  headers={'Content-type': 'application/json'})

    return redirect('/')



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
        'customer_id': customer_id
    }

    # Submit a transaction
    new_tx_address = "{}/new_transactions".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=product_object,
                  headers={'Content-type': 'application/json'})

    # Return to the homepage
    return redirect('/')


