from datetime import datetime

class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = datetime.now()
        self.block_hash = hash(str(self.previous_hash) + str(self.timestamp) + str(self.transactions.certificate.key))
        self.nonce = None

    def get_block_hash(self):
        return self.block_hash

    def get_transactions(self):
        return self.transactions

    def get_previous_hash(self):
        return self.previous_hash

    def to_string(self): #warning: remove private key from this after publishing
        return str(" Transactions: " + str(self.transactions.to_string()) + " Previous Hash: " + str(self.previous_hash) + " Timestamp: " + \
               str(self.timestamp) + " Hash: " + str(self.block_hash))


#class: Blockchain
#description: contains all blocks in the application.
class Blockchain:

    difficulty = 1

    def __init__(self):
        self.tail = None
        self.chain = [] # the blocks themselves are stored here
        self.unconfirmed_transactions = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(Transaction("Mike", "Computer", Certificate("Approved by Ryan the Tiger")))
        self.chain.append(genesis_block)

    #used to quickly index into the most recently added block in the chain.
    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction_to_pending(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def add_block(self, block, proof):
        previous_hash = self.last_block.get_block_hash()

        if previous_hash == self.last_block.get_block_hash():
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.previous_hash = proof
        self.chain.append(block)
        return True

    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.get_block_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.get_block_hash()

        return computed_hash

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.get_block_hash())

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block()

        new_block = Block(transactions=self.unconfirmed_transactions,
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.get_block_hash()


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
