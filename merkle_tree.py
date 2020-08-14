import hashlib
import blockchain.globals

hashes = []
queue = []
blocks = blockchain.globals.blockchain_tree

class Node:
    def __init__(self):
        self.left = None
        self.right = None
        self.hash = None

    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.right = right

    def set_hash(self, hash):
        self.hash = hash

    def get_hash(self):
        return self.hash

#function: compute_merkle_root
#description:
def compute_merkle_root():
    calculate_merkle_hashes()
    global hashes
    global queue

    while len(hashes) > 1:
        # repeatedly get first two blocks and hash them
        queue.append(hash(hashes[0].get_hash() + hashes[1].get_hash()))
        #add new nodes to queue
        #remove hashed blocks
        hashes.pop(0)
        hashes.pop(0)
    #move queue to hashes
    if (len(queue) == 1):
        print(queue[0])
        return queue[0]
    else:
        hashes = queue
        queue = []
        compute_merkle_root()
    #repeat above until one node remains

#function: calculate_merkle_hashes
#description: takes the linked list of blocks in the blockchain and adds them to the merkle tree. This DOES NOT calculate the merkle root
# or build anything of the merkle tree aside from the bottom layer.
def calculate_merkle_hashes():
    global blocks

    for block in blocks:
        n = Node()
        n.set_hash(block.get_block_hash())
        hashes.append(n)
    print(len(hashes))

