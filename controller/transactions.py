from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests, json
from view import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []
invoice_posts = []
errors = []
address = None


@app.route('/transactions')
def transactions_page():
    """Provides data for the index.html page on the front-end."""
    fetch_posts()
    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('transactions.html')

    return template.render(invoices=invoice_posts, node_address=CONNECTED_NODE_ADDRESS, errors=errors)


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data, and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    decrypt_url = "{}/decrypt".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    company_name = get_company_name()

    if response.status_code == 200:
        content = []
        invoices = []
        chain = json.loads(response.content)

        # iterate through each block and their transactions
        for block in chain["chain"]:
            content.append(block)
            for transaction in block["transactions"]:
                invoices.append(transaction)

        global posts
        global invoice_posts
        invoice_posts = invoices
        posts = content


def get_company_name():
    with open('model/peerdata.json', 'r') as file:
        data = json.loads(file.read())
        name = data["name"]
    return name


@app.route('/set_company', methods=['POST'])
def get_address_from_user():
    global address
    address = request.form["address"]

    return redirect('/transactions')


@app.route('/submit_public_key', methods=['POST'])
def set_public_key():

    key = request.form["key"]

    forward_address = "{}/set_public_key".format(CONNECTED_NODE_ADDRESS)

    requests.post(forward_address,
                  json=key,
                  headers={'Content-type': 'application/json'})

    return redirect('/transactions')