import os
import time
import sys
from fabric.api import task
from fabric.api import run
from cloudservers import CloudServers

"""
Rackspace Cloud Servers

Image IDs
--------------
100 : Arch 2011.10
126 : Fedora 17
108 : Gentoo 11.0
109 : openSUSE 12
89 : Windows Server 2008 R2 x64 - SQL2K8R2 Web
110 : Red Hat Enterprise Linux 5.5
85 : Windows Server 2008 R2 x64
120 : Fedora 16
91 : Windows 2008 R2 - Denali Std
119 : Ubuntu 11.10
122 : CentOS 6.2
104 : Debian 6 (Squeeze)
115 : Ubuntu 11.04
92 : Windows 2008 R2 - Denali Web
118 : CentOS 6.0
112 : Ubuntu 10.04 LTS
31 : Windows Server 2008 SP2 x86
24 : Windows Server 2008 SP2 x64
57 : Windows Server 2008 SP2 x64 - MSSQL2K8R2
121 : CentOS 5.8
111 : Red Hat Enterprise Linux 6
116 : Fedora 15
125 : Ubuntu 12.04 LTS
56 : Windows Server 2008 SP2 x86 - MSSQL2K8R2
86 : Windows Server 2008 R2 x64 - MSSQL2K8R2
114 : CentOS 5.6
103 : Debian 5 (Lenny)

Flavor IDs
--------------
1 : 256 server
2 : 512 server
3 : 1GB server
4 : 2GB server
5 : 4GB server
6 : 8GB server
7 : 15.5GB server
8 : 30GB server
"""

@task
def create_server():
    username = os.getenv('CLOUD_SERVERS_USERNAME')
    key = os.getenv('CLOUD_SERVERS_API_KEY')
    cs = CloudServers(username, key)
    suffix = os.urandom(8).encode('hex')

    files = {'/root/.ssh/authorized_keys': open(os.getenv('HOME')+"/.ssh/id_rsa.pub")}

    print('Creating instance Ubuntu 12.04 LTS')

    instance = cs.servers.create(image=125,
                                 flavor=1,
                                 files=files,
                                 name='webserver-{}'.format(suffix))

    instance_id = instance.id
    print('Waiting for instance to start...')

    status = instance.status

    spinner = ['|', '/', '-']
    spinner_index = 0
    sleep_index = 0

    while status != 'ACTIVE':
        time.sleep(.125)
        sleep_index = sleep_index + .125

        if sleep_index % 10.0:
            instance = cs.servers.get(instance_id)
            status = instance.status

        spinner_index = 0 if spinner_index == len(spinner) - 1 else spinner_index + 1
        spinner_str = spinner[spinner_index]

        if status == 'BUILD':
            if instance.progress == 100:
                message = "Running Post-Build Configurations {} ".format(spinner_str)
            else:
                message = "Building {} ".format(spinner_str)

        sys.stdout.write("\r" + message)
        sys.stdout.flush()

    if status == 'ACTIVE':
        sys.stdout.write("\r")
        sys.stdout.flush()
        public_ip = instance.addresses['public'][0]
        dns_name = "{}.static.cloud-ips.com".format(public_ip.replace('.', '-'))
        print('New instance {} ({}) accessible at {}'.format(instance.id, instance.name, dns_name))
    else:
        print('Instance status: ' + status)
        return
