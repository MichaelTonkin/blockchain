from datetime import datetime


class Block:
    def __init__(self, transaction, previoushash):
        self.transaction = transaction
        self.previousHash = previoushash
        self.timestamp = datetime.now()
        self.blockHash = hash(str(self.previousHash) + str(self.timestamp) + str(self.transaction.certificate.key))

    def get_block_hash(self):
        return self.blockHash

    def get_transaction(self):
        return self.transaction

    def get_previous_hash(self):
        return self.previousHash

    def to_string(self): #warning: remove private key from this after publishing
        return str(" Transaction: " + str(self.transaction.to_string()) + " Previous Hash: " + str(self.previousHash) + " Timestamp: " + \
               str(self.timestamp) + " Hash: " + str(self.blockHash))


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
