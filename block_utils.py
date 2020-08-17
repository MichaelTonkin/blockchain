from application.block import Block

def create_block(transaction, previousHash):
    new_block = Block(transaction, previousHash)
    blocks.blockchain_tree.append(new_block)


def blockchain_to_string():
    for item in blocks.blockchain_tree:
        print(item.to_string())


