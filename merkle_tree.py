import blockchain.globals
#I think we haven't set up a linked list properly
class Node:
    def __init__(self):
        self.left = None
        self.right = None
        self.hash = hash(self.left + self.right)

def build_merkle_tree():
