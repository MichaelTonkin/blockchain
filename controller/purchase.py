from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests, json
from view import app
from model.cryptography.rsa import load_public_key


feedback = []

@app.route('/purchase')
def load_purchase_page():
    global feedback

    env = Environment(
        loader=PackageLoader('view', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('purchase.html')

    return template.render(feedback=feedback)


def get_company_details():
    with open('model/peerdata.json', 'r') as file:
        data = json.loads(file.read())
    return data


def get_ia_node():
    with open('model/ia_address.json', 'r') as file:
            data = str(file.read())
    return data[1 : len(data)-1]


@app.route('/submit_purchase_req', methods=['POST'])
def make_purchase_request():
    global feedback
    #get updated peerlist from information agent

    feedback = []
    has_courier = False
    has_producer = False

    ia = get_ia_node()
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

    potential_amount = 0 # we use this variable to track the total amount of stock we can get from various producers
    amount = int(amount)

    for company in peerlist:
        if has_producer == True:
            break
        if item in company['products']:
            company_url = "{}/receive_purchase_req".format(company['node_address']+":8000")
            company_response = requests.post(company_url, json=json_data)
            try:
                print(company_response.json())
                if company_response.json()['accepted'] == True:
                    potential_amount += int(company_response.json()['stock'])
                    print("Nice. It's been accepted")
                    feedback.append({"company": company_response.json()['company'], "price": company_response.json()['price'],
                                    "stock": company_response.json()['stock']})
                    has_producer = True
            except:
                pass

            if potential_amount >= amount:
                break
    if potential_amount < amount:
        print("Could not find enough stock")
        feedback.append("Could not find enough stock.")

    for courier in peerlist:
        if has_courier == True:
            break
        if "Courier" in courier['company_type']:
            courier_url = "{}/receive_courier_req".format(courier['node_address'] + ":8000")
            courier_response = {}
            try:
                courier_response = requests.post(courier_url, json=json_data)
            except:
                pass
            try:
                if courier_response.json()['dates']:
                    feedback.append({"company": courier_response.json()['company'],
                                     "shipment_dates": courier_response.json()['dates']})
                    has_courier = True
            except:
                pass

    details = get_company_details()

    #add transaction to blockchain
    if has_courier and has_producer:
        requests.post(url="{}/new_transactions".format(ia),
                      json={
                          "company": details['name'],
                          "volume": amount,
                          "req_status": 'Request',
                          "item_type": item,
                          "starting_date": starting,
                          "ending_date": ending,
                          "frequency": frequency,
                      },
                      headers={'Content-type': 'application/json'})

    return redirect('/purchase')

