"""
This module contains the code for generating private and public keys.
We are using the RSA algorithm to do this.
"""
import sys, base64
from util import *
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey
from os import path
import os

priv_serial = None
private_key = None
public_key = None
public_key_name = ""


def set_public_key_name(name):
    global public_key_name
    public_key_name = name


def generate_private_key():
    """
    Generates the private key, used in decrypting a message.
    Should not be shared with any other nodes.
    """
    global private_key
    global priv_serial

    filename = "private_key.pem"
    #check if there is a private key on file. If so, use that.

    if path.exists(filename):
        private_key = load_private_key(filename)

    else:
        #generate the private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
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

    #priv_serial holds a serialized version of the public key.
    pub_serial = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    with open("public_key.pem", "wb") as key_file:
        key_file.write(pub_serial)

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


def encrypt(msg, custodian):
    """
    Encrypts a message in string format
    :param: msg - String
    :param: key - The public key used to encrypt the message
    """
    global public_key_name
    if custodian:
        public_key_name = "chain_custodian.pem"
    else:
        public_key_name = load_from_file("public_key_name.txt")

    mes = bytes(msg, 'utf8')

    if(public_key_name == ""):
        pub_key = load_public_key(os.path.relpath("model/public_keys/public_key.pem" + public_key_name))
    else:
        pub_key = load_public_key(os.path.relpath("model/public_keys/" + public_key_name))

    ciphertext = pub_key.encrypt(
        mes,
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

    cipher_pass = encrypted_msg

    try:
        decrypted_msg = private_key.decrypt(
            cipher_pass,
            padding.OAEP(
                mgf = padding.MGF1(algorithm=hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )
    except InvalidKey:
        print("Error - unable to decrypt message.")
        decrypted_msg = "Error - unable to decrypt message."

    return decrypted_msg


def load_private_key(filename):
    """
    Loads private key from a .pem file
    """
    with open(filename, "rb") as key_file:
        key = serialization.load_pem_private_key(
        key_file.read(),
        password = None,
        backend = default_backend()
        )
    return key


def load_public_key(filename):
    """
    Loads public key from a .pem file
    """
    with open(filename, "rb") as key_file:
        key = serialization.load_pem_public_key(
        key_file.read(),
        backend = default_backend()
        )
    return key

