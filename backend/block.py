import json
import base64
from backend.cryptography.rsa import encrypt, decrypt
from datetime import datetime
from hashlib import sha256

class Block:
    """
    The datastructure for a single block on the blockchain.
    """
    def __init__(self, transactions, previous_hash):
        self.transactions = []
        self.transactions_to_string_list(transactions)
        self.previous_hash = previous_hash
        self.timestamp = str(datetime.now())
        self.nonce = 0
        self.block_hash = self.calculate_block_hash()

    def calculate_block_hash(self):
        block_string = json.dumps(str(self.__dict__), sort_keys=True)
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



def quick_encrypt(msg):
    return base64.b64encode(encrypt(msg))

class Blockchain:
    """
    The data structure for the blockchain. Manages storing blocks, mining algorithm, validity and PoW.
    Do note that you will need to call blockchain.chain in order to access individual
    blocks.
    """
    difficulty = 1

    def __init__(self):
        self.tail = None
        self.chain = [] # the blocks themselves are stored here
        self.unconfirmed_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(transactions=[Transaction("UWE", quick_encrypt("500"), quick_encrypt("A0000"), "0").to_string()],
                              previous_hash="0000")

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
            return False

        if not Blockchain.is_valid_proof(self, block, proof):
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
                block_hash == block.get_block_hash())

    def mine(self):
        if not self.unconfirmed_transactions: #check that there is something to mine
            return False

        last_block = self.last_block

        new_transactions = []

        #generate a list of transactions
        for transaction in self.unconfirmed_transactions:
            new_transactions.append(Transaction(transaction["customer_id"], encrypt(transaction["weight"]),
                                                encrypt(transaction["initial_id"]), encrypt(transaction["manufacturer_id"])
                                                ).to_string())

        new_block = Block(transactions=new_transactions,
                          previous_hash=last_block.get_previous_hash())

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return new_block.get_block_hash()

    def check_chain_validity(cls, chain):
        """
        A helper method to check if the entire blockchain is valid.
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for block in chain:
            block_hash = block.get_block_hash()
            # remove the hash field to recompute the hash again
            # using "compute_hash" method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.get_block_hash()) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.get_block_hash, previous_hash = block_hash, block_hash

        return result


class Transaction:
    def __init__(self, receiver, weight, initID, manuID):
        self.receiver = receiver #the address of the node recieving this transaction
        self.initID = initID #initial product id
        self.manuID = manuID #manugacturer product id
        self.weight = weight
        self.timestamp = encrypt(str(datetime.now()))

    def to_string(self):
        return '{Date ' + str(self.timestamp) + ' Manufacturer_Product_ID ' + str(self.manuID) + ' Weight_KG ' + str(self.weight) \
               + ' Initial_Product_ID ' + str(self.initID) + ' Customer ' + str(self.receiver) + '}'
