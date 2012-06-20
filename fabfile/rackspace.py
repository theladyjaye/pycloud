import os
import time
import sys
from fabric.api import task
from fabric.api import run
from fabric.api import env
from fabric.api import settings
from fabric.api import run
from fabric.api import put
from fabric.api import local
from fabric.api import lcd
from fabric.colors import green
from fabric.colors import red
from fabric.colors import magenta
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
    dns_name = None
    spinner = ['|', '/', '-']
    spinner_index = 0
    sleep_index = 0

    files = {'/root/.ssh/authorized_keys': open(os.getenv('HOME')+"/.ssh/id_rsa.pub"),
             '/root/bootstrap.sh'        : open('{}/bootstrap/ubuntu.sh'.format(env.real_fabfile))}

    print(green("\nCreating instance Ubuntu 12.04 LTS\n", bold=True))
    instance = cs.servers.create(image=125,
                                 flavor=1,
                                 files=files,
                                 name='webserver-{}'.format(suffix))

    instance_id = instance.id

    print(magenta('Waiting for instance to start...'))

    status = instance.status

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

        sys.stdout.write("\r" + magenta(message))
        sys.stdout.flush()

    if status == 'ACTIVE':
        sys.stdout.write("\r")
        sys.stdout.flush()
        public_ip = instance.addresses['public'][0]
        dns_name = "{}.static.cloud-ips.com".format(public_ip.replace('.', '-'))
        print(green('New instance {} ({}) created!\nAccessible at {}'.format(instance.id, instance.name, dns_name), bold=True))
    else:
        print(red('Instance status: ' + status))
        return

    with(settings(host_string=dns_name, user='root')):
        # This is the fabric task for bootstrapping a running instance
        bootstrap()
        configuration_package()
        configuration_deliver()
        provision()

@task
def bootstrap():
    print(green('Bootstraping instance', bold=True))
    # We could just run run the commands here instead of
    # executing the bootstrap script but I like having the 
    # bootstrap script abstracted away for use with other
    # services.
    run('chmod u+x ./bootstrap.sh')
    run('./bootstrap.sh')

@task
def configuration_package():
    path = env.real_fabfile
     
    with lcd(path):
        local('rm -rf configuration.tgz'.format(path))
        local('tar -cvzf configuration.tgz ./configuration'.format(path))
        local('mv configuration.tgz ./configuration/'.format(path))

@task
def configuration_deliver():
    with(settings(host_string='108-166-65-222.static.cloud-ips.com', user='root')):
        path = env.real_fabfile
        put('{0}/configuration/configuration.tgz'.format(path), 'configuration.tgz')
        run('rm -rf ./configuration')
        run('tar -xzf ./configuration.tgz')

@task
def provision():
    with(settings(host_string='108-166-65-222.static.cloud-ips.com', user='root')):
        run("puppet apply --modulepath '/root/configuration/modules' /root/configuration/site.pp")