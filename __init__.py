from blockchain.block import *
from blockchain.block_utils import *
import blockchain.globals

if __name__ == "__main__":
    #create genesis block
    cert = Certificate("genesis")
    transaction = Transaction("Mike", "Bob", cert)

    cert2 = Certificate("le approve")
    transaction2 = Transaction("John", "Tim", cert2)

    create_block(transaction, "0000")

    index = len(g.blockchain_tree) - 1
    prevHash = g.blockchain_tree[index].blockHash

    create_block(transaction2, prevHash)

    blockchain_to_string()
