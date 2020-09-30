import sys

def load_address_from_file():
    with open("node_address.txt", "r") as file:
        address = file.read()
        file.close()
        return address

def load_from_file(file):
    with open(file, "r") as file:
        data = file.read()
        file.close()
        return data

def write_to_file(file, text):
    with open(file, "w+") as file:
        file.write(text)
        file.close()
    print("file write successful", sys.stdout)

