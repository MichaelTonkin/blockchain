def load_address_from_file():
    with open("node_address.txt", "r") as file:
        address = file.read()
        file.close()
        return address