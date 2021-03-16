class Peer:

    def __init__(self, name, company_type, products, ip, physical_address):
        self.name = name
        self.company_type = company_type
        self.products = products
        self.ip = ip
        self.physical_address = physical_address

    def to_json(self):
        data = {
            'name': self.name,
            'node_address': self.ip,
            'company_type': self.company_type,
            'products': self.products,
            'physical_address': self.physical_address
        }

        return data
