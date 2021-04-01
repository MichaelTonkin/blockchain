from model.block import Blockchain, Block
from model.cryptography.rsa import *
from flask import Flask, request
from model.peer import Peer
from model.supplieragent import SupplierAgent
import time, json, requests, sys, base64

app = Flask(__name__)
print("model is working", sys.stdout)
private_key = generate_private_key()
public_key = generate_public_key()
#initialize our blockchain as an object
blockchain = Blockchain()

current_ip = None

# Contains the host address of other participating members of this network
peers_json = {}
peers_json['nodes'] = []

#The internal data structure for the peers objects
peers = set()


@app.route('/remove_node', methods=['POST'])
def remove_node():
    """Removes a node from the peerlist.json file"""

    # The host address to the peer node
    name = request.get_json()["name"]
    node_address = request.get_json()["node_address"]
    company_type = request.get_json()["company_type"]
    physical_address = request.get_json()["physical_address"]

    if not node_address:
        return "Invalid data", 400

    node = {
        'name': name,
        'node_address': node_address,
        'company_type': company_type,
        'products': [],
        'physical_address': physical_address
    }

    # update the node if it already exists in the list
    if node in peers_json['nodes']:
        for company in peers_json['nodes'][0]:
            if company['name'] == name:
                company.update(node)
                break

    # add the node to the peer list
    peers_json['nodes'].append(node)

    with open('model/peerlist.json', 'w') as outfile:
        json.dump(peers_json, outfile)


@app.route('/receive_purchase_req', methods=['POST'])
def receive_purchase_req():
    data = request.get_json()
    print("dada" + str(data), sys.stdout)
    sa = SupplierAgent(product=data['item'], quantity=data['amount'], start_date=data['starting'],
                       end_date=data['ending'], frequency=data['frequency'])

    return sa.process_request(), 200


def load_peers_on_startup():
    """Here we loop through all the values in peerlist.json and convert it to a set"""
    if len(peers) <= 0:
        try:
            with open('model/peerlist.json') as data_file:
                data = json.load(data_file)

                for v in data.values():
                    print(v)
                    peers.add(Peer(name=v[0]['name'],
                                   company_type=v[0]['company_type'],
                                   products=v[0]['products'],
                                   ip=v[0]['node_address'],
                                   physical_address=v[0]['physical_address']))
        except:
            print("No data to load from peerlist.json")

load_peers_on_startup()

@app.route('/set_public_key', methods=['POST'])
def set_public_key():

    key_data = request.get_json()

    write_to_file("public_key_name.txt", key_data)
    return "Success", 201


@app.route('/new_transactions', methods=['POST'])
def new_transactions():
    """
    This is the endpoint for users to submit new transactions. It will add said transactions to the blockchain.
    """
    tx_data = request.get_json()
    required_fields = ["company"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

        tx_data["issue_date"] = time.time()
        blockchain.add_transaction_to_pending(tx_data)
        print(blockchain.unconfirmed_transactions)

        return "Success", 201


def block_to_json(block):
    """
    Converts the block passed into parameters into a json readable format.
    """

    transactions = []

    for transaction in block.get_transactions():
        transactions.append(transaction.to_string())

    return {"transactions": transactions, "previous_hash": block.get_previous_hash(),
                       "timestamp": block.timestamp, "nonce": block.nonce, "hash": block.get_block_hash()}


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    return the current node's copy of the blockchain in json format
    """
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block_to_json(block))

    return json.dumps({"length": len(chain_data),
                       "chain": chain_data})


@app.route('/pending_tx')
def get_pending_tx():
    """
    returns a list of transactions pending confirmation
    """
    return json.dumps(blockchain.unconfirmed_transactions)


@app.route('/register_node', methods=['POST'])
def register_new_peers():
    """
    End point to add new peers to the network
    """

    # The host address to the peer node
    name = request.get_json()["name"]
    node_address = request.get_json()["node_address"]
    company_type = request.get_json()["company_type"]
    products = request.get_json()["products"]
    physical_address = request.get_json()["physical_address"]

    if not node_address:
        return "Invalid data", 400

    new_node = {
        'name': name,
        'node_address': node_address,
        'company_type': company_type,
        'products': products,
        'physical_address': physical_address
    }

    with open('model/peerlist.json') as data_file:
        peers_json = json.load(data_file)

    # update the node if it already exists in the list
    for company in peers_json['nodes']:
        if company['name'] == name:
            company.update(new_node)

            with open('model/peerlist.json', 'w') as outfile:
                json.dump(peers_json, outfile)
            return get_chain()

    # add the node to the peer list
    peers_json['nodes'].append(new_node)

    with open('model/peerlist.json', 'w') as outfile:
        json.dump(peers_json, outfile)

    peers.add(Peer(name=name,
                   company_type=company_type,
                   products=products,
                   ip=node_address,
                   physical_address=physical_address))

    return get_chain()


@app.route('/update_peerslist', methods=['POST'])
def update_peerslist():
    """Called when a node wishes to receive the most up-to-date version of the peerlist.json file (which contains
    information about all nodes on the network)."""

    with open('model/peerlist.json', 'r') as file:
        data = file.read()

    json_data = json.loads(data)
    return json_data


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the "register_node" endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """

    name = request.get_json()["name"]
    node_address = request.get_json()["node_address"]
    company_type = request.get_json()["company_type"]
    products = request.get_json()["products"]
    physical_address = request.get_json()["physical_address"]
    target_node = request.get_json()["information_node"]

    if not node_address:
        return "Invalid data", 400

    data = {
            "name": name,
            "node_address": node_address,
            "company_type": company_type,
            "products": products,
            "physical_address": physical_address
            }
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(target_node + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers_json
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)

        peers_json.update(response.json()['peers'])

        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    bc = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(transactions=block_data["transactions"],
                      previous_hash=block_data["previous_hash"],
                      timestamp=block_data["timestamp"])
        proof = block_data['hash']
        if idx > 0:
            added = bc.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!")
        else:  # the block is a genesis block, no verification needed
            bc.chain.append(block)
    return bc


def consensus():
    """
    The consensus algorithm to determine which instance of the chain our network should use. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node.ip))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
              # Longer valid chain found!
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    """Endpoint to add a block mined by someone else to the node's chain. The node first verifies the block and then
    adds it to the chain."""

    block_data = request.get_json(force=True)

    block = Block(block_data["transactions"].to_string(),
                  block_data["previous_hash"])
    proof = block_data['block_hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer.ip)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.__dict__)


@app.route('/decrypt', methods=['POST'])
def decrypt_transaction():
    data = request.get_data()
    print("data = " + str(data), sys.stdout)
    data = base64.b64decode(data)
    decrypted = decrypt(data)
    print("decry = " + str(decrypted), sys.stdout)
    return decrypted

