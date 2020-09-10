"""
This module contains the code for generating private and public keys.
We are using the RSA algorithm to do this.
"""
import sys
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from os import path

keys = []

def generate_private_key():
    """
    Generates the private key, used in decrypting a message.
    Should not be shared with any other nodes.
    """
    global private_key
    filename = "private_key.pem"
    #check if there is a private key on file. If so, use that.

    if path.exists(filename):
        private_key = load_key(filename)

    else:
        #generate the private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        #priv_serial holds a serialized version of the private key.
        priv_serial = private_key.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )

        with open("private_key.pem", "wb") as key_file:
            key_file.write(priv_serial)


def generate_public_key():
    """
    Generates a public key from the private key.
    Used in encrypting messages to be sent to node with the corresponding private key.
    """
    global public_key
    public_key = private_key.public_key()


def load_address_from_file():
    with open("node_address.txt", "r") as file:
        address = file.read()
        file.close()
        return address


def generate_address():
    """
    Generates this node's address by encrypting the public key.
    Will generate a new public key if one doesn't exist.
    """
    if(public_key in globals()):
        address = sha256(str(public_key).encode('utf-8')).hexdigest()
    else:
        generate_public_key()
        address = sha256(str(public_key).encode('utf-8')).hexdigest()
    write_to_file("node_address.txt", str(address))
    return str(address)


def write_to_file(file, data):
    f = open(file, "w+")
    f.write(data)
    f.close()


def encrypt(msg):
    """
    Encrypts a message in string format
    :param: msg - String
    """
    mes = bytes(msg, 'utf8')
    ciphertext = public_key.encrypt(
        mes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return str(ciphertext)


def decrypt(encrypted_msg):
    """
    Decrypts a message in string format
    :param: encrypted_msg - an encrypted message
    """
    print(encrypted_msg, sys.stdout)

    decrypted_msg = private_key.decrypt(
        encrypted_msg,
        padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None
        )
    )
    return decrypted_msg


def load_key(filename):
    """
    Loads public or private key from a .pem file
    """
    with open(filename, "rb") as key_file:
        key = serialization.load_pem_private_key(
        key_file.read(),
        password = None,
        backend = None
        )
    return key



