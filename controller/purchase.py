from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests, json
from view import app
from model.supplieragent import SupplierAgent

@app.route('/purchase')
def load_purchase_page():

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('purchase.html')

    return template.render()


@app.route('/receive_purchase_req')
def receive_purchase_req():
    data = request.get_json()

    sa = SupplierAgent(product=data['item'], quantity=data['amount'], start_date=data['starting'],
                       end_date=data['ending'], frequency=data['frequency'])

    return sa.process_request()

@app.route('/submit_purchase_req', methods=['POST'])
def make_purchase_request():

    company_response = None

    #get updated peerlist from information agent

    ia = request.form['ia']
    item = request.form['item']
    amount = request.form['amount']
    frequency = request.form['frequency']
    starting = request.form['starting']
    ending = request.form['ending']

    json_data = {
        'item': item,
        'amount': amount,
        'frequency': frequency,
        'starting': starting,
        'ending': ending
    }

    ia_url = "{}/update_peerslist".format(ia)
    peerlist = requests.post(ia_url)

    #find first peer that has the item we want
    peerlist = peerlist.json().get('nodes')
    print(peerlist)

    for company in peerlist:
        if item in company['products']:
            company_url = "{}/receive_product_req".format(company['node_address'])
            company_response = requests.post(company_url, json=json_data)
            break

    #send request

    #do something if request can be partly fullfilled
    print(company_response)

    #if we have all the items, contact couriers

    #if request is rejected go to next peer with item we want

    #if no one can accept our request, apologise profusely

    return redirect('/purchase')