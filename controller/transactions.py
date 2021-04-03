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

    template = env.get_template('index.html')

    return template.render(invoices=invoice_posts, node_address=CONNECTED_NODE_ADDRESS, errors=errors)


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
                customer_pos = transaction.find("Company") #get the customer id from transaction
                if customer_pos is not -1:
                    customer = transaction[customer_pos + 8:]
                    customer = customer[0:customer.find(" ")]
                    print(customer)
                    if customer == address:
                        encrypted = transaction.split(" ")
                        decrypt_response = [] #holds segments of the invoice which need to be decrypted.
                        for i in range(1, 9, 2):
                            decrypt_response.append(requests.post(decrypt_url, data=encrypted[i][1:]))
                        #construct decrypted transaction
                        item1 = decrypt_response[0].content.decode('utf-8')
                        item2 = decrypt_response[1].content.decode('utf-8')
                        item3 = decrypt_response[2].content.decode('utf-8')
                        item4 = decrypt_response[3].content.decode('utf-8')
                        inv = {"Date": item1, "Manufacturer Product ID": item2,
                               "Weight (KG)": item3, "Initial Product ID": item4}
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