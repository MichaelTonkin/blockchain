from flask import redirect
from backend.interface import *
from jinja2 import Environment, PackageLoader, select_autoescape
import sys
from frontend import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"
posts = []

@app.route('/')
def index_page():
    """Provides data for the index.html page on the front-end."""
    fetch_posts()
    env = Environment(
        loader=PackageLoader('frontend', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')

    return template.render(posts=posts, node_address=CONNECTED_NODE_ADDRESS)


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data, and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)

    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            content.append(block)

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


