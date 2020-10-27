from backend.block import Blockchain, Block
from backend.cryptography.rsa import *
from flask import Flask, request
import time, json, requests, sys, base64, threading, zlib

app = Flask(__name__)
print("backend is working", sys.stdout)
#get our private and public keys
private_key = generate_private_key()
public_key = generate_public_key()
#initialize our blockchain as an object
blockchain = Blockchain()
blockchain.create_genesis_block()

current_ip = None

# Contains the host address of other participating members of this network
peers = set()


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
    required_fields = ["initial_id", "weight", "customer_id"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

        tx_data["timestamp"] = time.time()
        blockchain.add_transaction_to_pending(tx_data)
        return "Success", 201


def block_to_json(block):
    """
    Converts the block passed into parameters into a json readable format.
    """

    transactions = []

    for transaction in block.get_transactions():
        transactions.append(str(transaction))

    return {"transactions": block.transactions,
                       "timestamp": block.timestamp, "nonce": block.nonce, "block_hash": block.block_hash}


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    return the current node's copy of the blockchain in json format
    """
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__) #TODO block.__dict__?

    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})

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
    global current_ip

    # The host address to the peer node
    node_address = request.get_json()["node_address"]
    contacted_address = request.get_json()["contacted_address"]

    current_ip = contacted_address
    print("current ip = " + str(current_ip), sys.stdout)

    if not node_address:
        return "Invalid data", 400

    # add the node to the peer list
    #TODO ensure there are no duplicates
    peers.add(node_address)
    peers.add(contacted_address)

    #announce the updated list of peers to the network
    announce_new_peers()

    return get_chain()


@app.route('/update_peers', methods=['POST'])
def update_peers():
    global peers
    global current_ip
    new_peers = request.get_json()
    print("current ip = " + str(current_ip), sys.stdout)
    print("updated peers = " + str(new_peers), sys.stdout)
    peers = set(new_peers)

    return '/'


def announce_new_peers():
    """Sends a list of peers across the network"""
    global current_ip

    for peer in peers:
        if peer != current_ip:
            url = "{}update_peers".format(peer)
            print("updating peers for: " + str(url), sys.stdout)
            headers = {'Content-Type': "application/json"}
            requests.post(url, data=json.dumps(list(peers)), headers=headers)


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the "register_node" endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    global current_ip
    contacted_address = request.get_json()["node_address"]

    if not contacted_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url, "contacted_address": contacted_address}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(contacted_address + "register_node",
                             data=json.dumps(data), headers=headers)

    current_ip = request.host_url

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)

        peers.update(response.json()['peers'])

        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    bc = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(transactions=block_data["transactions"],
                      timestamp=block_data["timestamp"],
                      previous_hash=block_data["previous_hash"])
        block.block_hash = block_data["block_hash"]
        proof = block_data["block_hash"]

        if idx > 0:
            added = bc.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!")
        else:  # the block is a genesis block, no verification needed
            bc.chain.append(block) #TODO are you sure this makes sense?
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
        response = requests.get('{}chain'.format(node))
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

    print("New block received from network...", sys.stdout)

    block_data = request.get_json(force=True)
    print(block_data, sys.stdout)
    block = Block(transactions=block_data["transactions"],
                  timestamp=block_data["timestamp"],
                  previous_hash=block_data["previous_hash"]
                  )
    block.block_hash = block_data["block_hash"]
    #TODO why are we generating the block hash once and then redefining it? Stupid.
    proof = block_data['block_hash']
    added = blockchain.add_block(block, proof)

    if not added:
        print("block discarded by node", sys.stdout)
        return "The block was discarded by the node", 400

    print("block added to chain", sys.stdout)
    return "Block added to the chain", 201


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    args = 1
    print("current ip = " + str(current_ip), sys.stdout)
    for peer in peers:
        if peer != current_ip:
            url = "{}add_block".format(peer)
            print("adding block @ " + str(url), sys.stdout)
            headers = {'Content-Type': "application/json"}
            x = threading.Thread(target=announce_new_block_helper(
                                url=url, block=block, headers=headers
                                )
                                 , args=(args,))
            x.start()
            x.join()
            args += 1
            print("Request to add block finished sending", sys.stdout)


def announce_new_block_helper(url, block, headers):
    try:
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers, verify=True, timeout=60)
    except requests.Timeout:
        print("request timed out though block may have still reached its destination", sys.stdout)


#sort_keys=False put it in json.dumps
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    global blockchain

    result = blockchain.mine()
    if not result:
        print("No transactions to mine", sys.stdout)
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
    data = base64.b64decode(data)
    decrypted = decrypt(data)
    return decrypted
