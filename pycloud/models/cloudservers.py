from pycloud.utils.collections import AttributeDict
class CloudServer(AttributeDict):
    def __init__(self):
        self.id = None
        self.label = None
        self.dns_name = None
        self.ip_address = None
