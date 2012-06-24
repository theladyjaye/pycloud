import time
import sys
import socket
from fabric.api import task
from fabric.api import settings
from fabric.api import local
from fabric.api import lcd
from fabric.api import env
from fabric.api import run
from fabric.api import put
from fabric.colors import magenta
from fabric.colors import red
from fabric.colors import white
from pycloud.services.cloudservers import CloudServerService
from pycloud.providers.amazon import EC2

@task
def create():
    user_data = None

    with open('{}/bootstrap/ubuntu.sh'.format(env.real_fabfile)) as f:
        user_data = f.read()

    service = CloudServerService(provider=EC2())
    server = service.create(image_id='ami-a29943cb',
                            type_id='t1.micro',
                            key_name='id_rsa.pub',
                            placement='us-east-1a',
                            security_groups=['default', 'webservers', 'ping'],
                            user_data=user_data,
                            instance_initiated_shutdown_behavior='terminate',
                            tags={'project':'test'})

    with(settings(host_string=server.dns_name, user='ubuntu')):
        message = 'Waiting for host to become available.'
        while 1:
            try:
                sys.stdout.write("\r" + magenta(message) + " ")
                sys.stdout.flush()
                sock = socket.create_connection((server.ip_address, 22), timeout=1)
                sock.close()
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            except IOError:
                message = message + '.'
                time.sleep(.500)

        configuration_package()
        configuration_deliver()

@task
def active():
    service = CloudServerService(provider=EC2())
    servers = service.get_servers(filters={'instance-state-name':'running', 'tag:project':'test'})

    for server in servers:
        print(server)

@task
def terminate(ids):
    service = CloudServerService(provider=EC2())
    service.terminate_servers(ids)


def configuration_package():

    print(magenta('Packaging Configuration'))
    path = env.real_fabfile

    with lcd(path):
        local('rm -rf configuration.tgz'.format(path))
        local('tar -czf configuration.tgz ./configuration'.format(path))
        local('mv configuration.tgz ./configuration/'.format(path))

def configuration_deliver():
    print(magenta('Delivering Configuration'))
    path = env.real_fabfile
    put('{0}/configuration/configuration.tgz'.format(path), 'configuration.tgz')
    run('rm -rf ./configuration')
    run('tar -xzf ./configuration.tgz')
