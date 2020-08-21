import sys
import json
from datetime import datetime
from hashlib import sha256

class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = datetime.now()
        self.nonce = None
        #TODO fix the fact that this is immutable
        self.block_hash = self.calculate_block_hash() #+ str(self.transactions.certificate.key))

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

    def get_previous_hash(self):
        return self.previous_hash

    def to_string(self): #warning: remove private key from this after publishing
        return str(" Transactions: " + str(self.transactions.to_string()) + " Previous Hash: " + str(self.previous_hash) + " Timestamp: " + \
               str(self.timestamp) + " Hash: " + str(self.block_hash))


#class: Blockchain
#description: contains all blocks in the backend.
class Blockchain:

    difficulty = 1

    def __init__(self):
        self.tail = None
        self.chain = [] # the blocks themselves are stored here
        self.unconfirmed_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(transactions=Transaction("Mike", "Computer", Certificate("Approved by Ryan the Tiger")),
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

        #if we do not have a valid proof, return false
        if not Blockchain.is_valid_proof(self, block, proof):
            return False
        print("Chain length = " + str(len(self.chain)), file=sys.stdout)

        block.previous_hash = proof
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
        print(block_hash + " + " + block.get_block_hash())
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.get_block_hash())

    def mine(self):
        if not self.unconfirmed_transactions: #check that there is something to mine
            return False

        last_block = self.last_block

        new_block = Block(transactions=self.unconfirmed_transactions,
                          previous_hash=last_block.get_previous_hash)

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
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.get_block_hash()) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.get_block_hash, previous_hash = block_hash, block_hash

        return result


class Transaction:
    def __init__(self, sender, receiver, certificate):
        self.sender = sender
        self.receiver = receiver
        self.timestamp = datetime.now()
        self.certificate = certificate

    def get_sender(self):
        return self.sender

    def get_receiver(self):
        return self.receiver

    def get_certificate(self):
        return self.certificate

    def to_string(self):
        return str(self.sender) + " Transferred " + str(self.certificate.to_string()) + " to " + str(self.receiver) + " at " + \
               str(self.timestamp)


class Certificate:
    def __init__(self, data):
        self.data = data
        self.key = hash(self.data)

    def to_string(self):
        return str(self.key)