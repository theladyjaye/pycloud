import os
import sqlite3
from pycloud.models.cloudservers import CloudServer

class CloudServerSqlite(object):

    def __init__(self, path='./'):
        db = '{}/pycloud.db'.format(path)
        needs_init = False

        if not os.path.isfile(db):
            needs_init = True

        self.conn = sqlite3.connect(db)

        if needs_init:
            self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE servers (id text,
                                           label text,
                                           dns_name text,
                                           ip_address text,
                                           provider text)''')

        self.conn.commit()
        c.close()

    def save(self, cloudserver):
        c = self.conn.cursor()
        c.execute('INSERT INTO servers VALUES(?,?,?,?,?)',(cloudserver.id,
                                                          cloudserver.label,
                                                          cloudserver.dns_name,
                                                          cloudserver.ip_address,
                                                          cloudserver.provider))
        self.conn.commit()
        c.close()

    def get_active(self):
        results = []
        c = self.conn.cursor()
        for row in c.execute('SELECT id, label, dns_name, ip_address, provider from servers'):
            server = CloudServer()
            server.id = row['id']
            server.label = row['label']
            server.dns_name = row['dns_name']
            server.ip_address = row['ip_address']
            server.provider = row['provider']
            results.append(server)

        c.close()
        return results
