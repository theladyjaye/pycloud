class CloudServerService(object):
    def __init__(self, provider):
        self.provider = provider

    def create(self, image_id, type_id, **kwargs):
        self.provider.create(image_id, type_id, **kwargs)

    def get_servers(self, filters=None):
        return self.provider.get_servers(filters)

    def terminate_servers(self, ids):
        self.provider.terminate_servers(ids)

