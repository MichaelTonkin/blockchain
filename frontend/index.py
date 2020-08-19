import datetime
import json
import requests
from flask import render_template, redirect, request
from backend.interface import *
from jinja2 import Environment, PackageLoader, select_autoescape

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:5000"

posts = []


@app.route('/')
def index_page():
    """The HTML code for the front-end user interface."""

    env = Environment(
        loader=PackageLoader('frontend', 'templates'), #lookup templates in the 'frontend' package
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('index.html')

    return template.render(posts=posts, node_address=CONNECTED_NODE_ADDRESS,)


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
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content,
                       key=lambda k: k['timestamp'],
                       reverse=True)




@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application
    """
    post_content = request.form["content"]

    post_object = {
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transactions".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    # Return to the homepage
    print(post_content, file=sys.stdout)
    return redirect('/')


