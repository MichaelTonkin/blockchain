from blockchain.block import Block
import blockchain.globals

g = blockchain.globals

def create_block(transaction, previousHash):
    new_block = Block(transaction, previousHash)
    g.blockchain_tree.append(new_block)


def blockchain_to_string():
    for item in g.blockchain_tree:
        print(item.to_string())


