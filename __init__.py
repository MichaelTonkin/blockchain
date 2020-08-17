from flask import Flask, request
from application.block import Blockchain
import time
import json
import requests

#Module:
#Description: using the flask library we create a server which is used to submit new transactions to the blockchain.

#initialize flask application
app = Flask(__name__)

#initialize our blockchain as an object
blockchain = Blockchain()

#using flask we create an endpoint which can be used by the application to add new transactions
#TODO come back and make sure this aligns with our actual block and blockchain data structure
@app.route('/new_transactions', methods=['POST'])
def new_transactions():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

        tx_data["timestamp"] = time.time()

        blockchain.add_transaction_to_pending(tx_data)

        return "Success", 201

#return the current node's copy of the chain.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


#end point to request a node to mine any existing unconfirmed transactions
@app.route('\mine', method=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)

@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)