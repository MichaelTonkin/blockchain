from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import requests, json
from view import app


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
    #get updated peerlist from information agent

    ia = request.form['ia']
    url = "{}update_peerslist".format(ia)
    peerlist = requests.post(url)

    #find first peer that has the item we want


    #send request

    #if request is rejected go to next peer with item we want

    #if no one can accept our request, apologise profusely

    return redirect('/purchase')