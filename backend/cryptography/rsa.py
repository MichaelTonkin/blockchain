"""
This module contains the code for generating private and public keys.
We are using the RSA algorithm to do this.
"""
import util
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


def generate_private_key():
    """
    Generates the private key, used in decrypting a message.
    Should not be shared with any other nodes.
    """
    global private_key
    keys = util.read_from_csv("keys")
    if(len(keys) > 1):
        private_key = keys[0]
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        util.write_to_csv(str(private_key), "keys")

def generate_public_key():
    """
    Generates a public key from the private key.
    Used in encrypting messages to be sent to node with the corresponding private key.
    """
    global public_key
    keys = util.read_from_csv("keys")
    if(len(keys) > 1):
        public_key = keys[1]
    else:
        public_key = private_key.public_key()
        util.write_to_csv(str(private_key), "keys")


def encrypt(msg):
    """
    Encrypts a message in string format
    :param: msg - String
    """
    msg = b'' + bytes(msg, 'utf8')
    ciphertext =  public_key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


def decrypt(encrypted_msg):
    """
    Decrypts a message in string format
    :param: encrypted_msg - an encrypted message
    """
    decrypted_msg = private_key.decrypt(
        encrypted_msg,
        padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None
        )
    )
    return decrypted_msg

