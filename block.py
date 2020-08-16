from datetime import datetime

class Block:
    def __init__(self, transaction):
        self.transaction = transaction
        self.previous_hash = None
        self.timestamp = datetime.now()
        self.block_hash = hash(str(self.previous_hash) + str(self.timestamp) + str(self.transaction.certificate.key))

    def get_block_hash(self):
        return self.block_hash

    def get_transaction(self):
        return self.transaction

    def get_previous_hash(self):
        return self.previous_hash

    def to_string(self): #warning: remove private key from this after publishing
        return str(" Transaction: " + str(self.transaction.to_string()) + " Previous Hash: " + str(self.previous_hash) + " Timestamp: " + \
               str(self.timestamp) + " Hash: " + str(self.block_hash))


#class: Blockchain
#description: contains all blocks in the blockchain.
class Blockchain:
    def __init__(self):
        self.tail = None
        self.chain = [] # the blocks themselves are stored here
        self.create_genesis_block()
        self.difficulty = 0
    def create_genesis_block(self):
        genesis_block = Block(Transaction("Mike", "Computer", Certificate("Approved by Ryan the Tiger")))
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.get_block_hash()

        if ( previous_hash == self.last_block.get_block_hash() ) :
            return False

        if ( not Blockchain.is_valid_proof(block, proof) ):
            return False

        block.previous_hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())


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
