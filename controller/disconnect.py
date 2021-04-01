from flask import request, redirect,render_template
from jinja2 import Environment, PackageLoader, select_autoescape
import sys, base64, requests, json, socket
from view import app


@app.route('/disconnect')
def disconnect():
    """Removes node from the network"""
    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    address = s.getsockname()[0]
    s.close()

    company_details = {
        'name': request.form["name"],
        'company_type': request.form["company_type"],
        'physical_address': request.form["physical_address"],
        'node_address': "http://" + address,
        'information_node': request.form["information_node"],
        'products': []
    }

    ia = request.form["information_node"]

    registration_address = "{}/remove_node".format(ia)

    requests.post(registration_address,
                  json=company_details,
                  headers={'Content-type': 'application/json'})

    template = env.get_template('index.html')

    return template.render()