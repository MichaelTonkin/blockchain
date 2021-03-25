from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests, json, sys
from view import app
#from model.supplieragent import SupplierAgent

@app.route('/purchase')
def load_purchase_page():

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('purchase.html')

    return template.render()

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

    potential_amount = 0 # we use this variable to track the total amount of stock we can get from various producers
    amount = int(amount)

    for company in peerlist:
        if item in company['products']:
            company_url = "{}/receive_purchase_req".format(company['node_address']+":8000")
            company_response = requests.post(company_url, json=json_data)
            if company_response.json()['accepted']:
                potential_amount += int(company_response.json()['stock'])
                print("Nice. It's been accepted")
            if potential_amount >= amount:
                break
    if potential_amount < amount:
        print("Could not find enough stock")
    #do something if request can be partly fullfilled
    #print("response = " +str(company_response.__dict__))

    #if request is rejected go to next peer with item we want

    #if no one can accept our request, apologise profusely

    #search for a courier who can handle the request

    return redirect('/purchase')