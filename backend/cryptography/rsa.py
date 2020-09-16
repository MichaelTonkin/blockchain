"""
This module contains the code for generating private and public keys.
We are using the RSA algorithm to do this.
"""
import sys, base64
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from os import path
import os

priv_serial = None
private_key = None
public_key = None

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
            backend=None
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


def encrypt(msg):
    """
    Encrypts a message in string format
    :param: msg - String
    :param: key - The public key used to encrypt the message
    """
    mes = bytes(msg, 'utf8')

    pub_key = load_public_key(os.path.relpath("backend/public_keys/public_key.pem"))

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
    decrypted_msg = private_key.decrypt(
        cipher_pass,
        padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None
        )
    )
    return decrypted_msg


def load_private_key(filename):
    """
    Loads private key from a .pem file
    """
    with open(filename, "rb") as key_file:
        key = serialization.load_pem_private_key(
        key_file.read(),
        password = None,
        backend = None
        )
    return key


def load_public_key(filename):
    """
    Loads public key from a .pem file
    """
    with open(filename, "rb") as key_file:
        key = serialization.load_pem_public_key(
        key_file.read()
        )
    return key


"""
generate_private_key()
generate_public_key()
test1 = "hello"
test2 = encrypt(test1)
print(decrypt(test2))
"""