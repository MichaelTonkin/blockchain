from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests
from view import app
import pandas as pd

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


@app.route('/submit_purchase_req', methods=['POST'])
def make_purchase_request():
    global feedback
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

    potential_amount = 0 # we use this variable to track the total amount of stock we can get from various producers
    amount = int(amount)

    for company in peerlist:
        if item in company['products']:
            company_url = "{}/receive_purchase_req".format(company['node_address']+":8000")
            company_response = requests.post(company_url, json=json_data)
            print(company_response.json())
            if company_response.json()['accepted'] == True:
                potential_amount += int(company_response.json()['stock'])
                print("Nice. It's been accepted")

                feedback.append(company_response.json())

            if potential_amount >= amount:
                break
    if potential_amount < amount:
        print("Could not find enough stock")
    #do something if request can be partly fulfilled
    #print("response = " +str(company_response.__dict__))

    #if request is rejected go to next peer with item we want

    #if no one can accept our request, apologise profusely

    #search for a courier who can handle the request

    #here we generate a dictionary which will be used as the transport calendar
    dates = pd.date_range(start=starting, end=ending)
    l = []
    for i in range(0, len(dates)):
        l.append(False)
    calendar = dict(zip(dates, l))


    for courier in peerlist:
        if "Courier" in courier['company_type']:
            courier_url = "{}/receive_courier_req".format(courier['node_address'] + ":8000")
            courier_response = requests.post(courier_url, json=json_data, data=calendar)
            if courier_response.json()['accepted']:
                feedback.append(courier_response.json())

                #add transaction to blockchain





    return redirect('/purchase')