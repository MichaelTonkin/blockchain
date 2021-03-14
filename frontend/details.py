from flask import request, redirect,render_template
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json
from frontend import app

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

@app.route('/details')
def index_page():
    """Provides data for the index.html page on the front-end."""
    env = Environment(
        loader=PackageLoader('frontend', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('details.html')

    return template.render(node_address=CONNECTED_NODE_ADDRESS)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application
    """

    product_object = {
        'company': request.form["company"],
        'req_status': request.form["req_status"],
        'volume': request.form["volume"],
        'item_type': request.form["item_type"],
        'starting_date': request.form["starting_date"],
        'ending_date': request.form["ending_date"],
        'frequency': request.form["frequency"]
    }

    # Submit a transaction
    new_tx_address = "{}/new_transactions".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=product_object,
                  headers={'Content-type': 'application/json'})

    # Return to the homepage
    return redirect('/')
