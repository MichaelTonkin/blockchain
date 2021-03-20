import json, sys, base64
from model.cryptography.rsa import encrypt
from datetime import datetime
from hashlib import sha256

class Block:
    """
    The datastructure for a single block on the blockchain.
    """
    def __init__(self, transactions, timestamp, previous_hash):
        self.transactions = transactions
        #self.transactions_to_string_list(transactions)
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.nonce = 0
        self.block_hash = None

    def calculate_block_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        hash = sha256(block_string.encode()).hexdigest()
        self.block_hash = hash
        return hash

    def set_transactions(self, transactions):
        self.transactions = transactions

    def get_block_hash(self):
        return str(self.block_hash)

    def get_transactions(self):
        return self.transactions

    def transactions_to_string_list(self, transactions):
        for transaction in transactions:
            if type(transaction) == str:
                self.transactions.append(transaction)
            else:
                self.transactions.append(transaction)

    def get_previous_hash(self):
        return self.previous_hash

    def to_string(self):
        return str(" Transactions: " + str(self.transactions) + " Previous Hash: " + str(self.previous_hash) + " Timestamp: " + \
               str(self.timestamp) + " Hash: " + str(self.block_hash))


def quick_encrypt(msg, custodian):
    """Applies encoding to encryption function to allow it to pass through the network.
    Parameters:
        String msg - The string to encrypt
        Boolean custodian - true if we want to use the chain custodian's public key rather than a user defined one.
        """
    return base64.b64encode(encrypt(msg, custodian))


class Blockchain:
    """
    The data structure for the blockchain. Manages storing blocks, mining algorithm, validity and PoW.
    Do note that you will need to call blockchain.chain in order to access individual
    blocks.
    """
    difficulty = 1

    def __init__(self):
        self.tail = None
        self.chain = []
        self.unconfirmed_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(transactions=[Transaction("Genesis", quick_encrypt("500", True), quick_encrypt("A0000", True),
                                                        quick_encrypt("BA0000", True), quick_encrypt(str(datetime.now()), True))
                              .to_string()],
                              previous_hash="0000",
                              timestamp=str(datetime.now()))
        genesis_block.calculate_block_hash()
        self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    #used to quickly index into the most recently added block in the chain.
    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction_to_pending(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def add_block(self, block, proof):
        previous_hash = self.last_block.get_block_hash()

        if previous_hash != self.last_block.get_block_hash():
            print("Previous hash is incorrect", sys.stdout)
            return False

        if not Blockchain.is_valid_proof(self, block, proof):
            print("proof is invalid", sys.stdout)
            return False

        block.previous_hash = previous_hash
        self.chain.append(block)
        return True

    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.get_block_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.calculate_block_hash()

        return computed_hash

    def is_valid_proof(self, block, block_hash):
        """
        check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == self.proof_of_work(block))

    def mine(self):
        if not self.unconfirmed_transactions: #check that there is something to mine
            return False

        last_block = self.last_block

        new_transactions = []
        #generate a list of transactions
        for transaction in self.unconfirmed_transactions:

            #We need to create a separate clone transaction that can be read by the chain custodian.
            new_transactions.append(Transaction(transaction["customer_id"],
                                                quick_encrypt(transaction["weight"], False),
                                                quick_encrypt(transaction["initial_id"], False),
                                                quick_encrypt(transaction["manufacturer_id"], False),
                                                quick_encrypt(str(datetime.now()), False)
                                                ).to_string())

            new_transactions.append(Transaction("Chain_Custodian",
                                                quick_encrypt(transaction["weight"], True),
                                                quick_encrypt(transaction["initial_id"], True),
                                                quick_encrypt(transaction["manufacturer_id"], True),
                                                quick_encrypt(str(datetime.now()), True)
                                                ).to_string())

        new_block = Block(transactions=new_transactions,
                          timestamp=str(datetime.now()),
                          previous_hash=last_block.get_previous_hash())
        new_block.calculate_block_hash()

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return new_block.get_block_hash()

    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.
        """
        result = True
        previous_hash = "0000"

        # Iterate through every block
        for block in chain:
            #we create a new block for ease of use as in some cases the data passed to chain may be in string format.
            new_block = Block(transactions=block["transactions"], timestamp=block["timestamp"],
                              previous_hash=block["previous_hash"])
            new_block.block_hash = block["block_hash"]
            block_hash = block["block_hash"]

            if not cls.is_valid_proof(new_block, block_hash) or \
                    previous_hash != new_block.previous_hash:
                print("Error - previous hash is incorrect or proof is invalid", sys.stdout)
                result = False
                break

            previous_hash = block_hash

        return result


class Transaction:
    def __init__(self, receiver, weight, initID, manuID, timestamp):
        self.receiver = receiver #the address of the node recieving this transaction
        self.initID = initID #initial product id
        self.manuID = manuID #manugacturer product id
        self.weight = weight
        self.timestamp = timestamp

    def to_string(self):
        return '{Date ' + str(self.timestamp) + ' Manufacturer_Product_ID ' + str(self.manuID) + ' Weight_KG ' + str(self.weight) \
               + ' Initial_Product_ID ' + str(self.initID) + ' Customer ' + str(self.receiver) + '}'
