from blockchain.block import *
from blockchain.block_utils import *
from blockchain.merkle_tree import *
import blockchain.globals

if __name__ == "__main__":

    blocks = blockchain.globals.blockchain_tree

    #create genesis block
    cert = Certificate("genesis")
    transaction = Transaction("Mike", "Bob", cert)

    cert2 = Certificate("le approve")
    transaction2 = Transaction("John", "Tim", cert2)

    cert3 = Certificate("le prove")
    transaction3 = Transaction("John", "Tim", cert3)

    create_block(transaction, "0000")

    index = len(blocks) - 1
    prevHash = blocks[index].blockHash

    create_block(transaction2, prevHash)

    index = len(blocks) - 1
    prevHash = blocks[index].blockHash

    create_block(transaction3, prevHash)

    blockchain_to_string()

    create_globals()
    compute_merkle_root()

