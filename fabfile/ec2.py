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
from fabric.api import sudo
from fabric.api import hide
from fabric.colors import magenta
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
                            security_groups=['default', 'webservers'],
                            user_data=user_data,
                            instance_initiated_shutdown_behavior='terminate',
                            tags={'project':'ctflorals'})

    with(settings(host_string=server.dns_name, user='ubuntu')):
        message = 'Waiting for host to become available'

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
                message = message + white('.')
                time.sleep(.750)

        # not using a puppet master
        configuration_package()
        configuration_deliver()
        provision()

@task
def active():
    service = CloudServerService(provider=EC2())
    servers = service.get_servers(filters={'instance-state-name':'running', 'tag:project':'ctflorals'})

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

def provision():
    print(magenta('Starting Provisioning'))
    message = 'Waiting for puppet to become available'

    with hide('everything'):
        with settings(warn_only=True):
            while 1:
                sys.stdout.write("\r" + magenta(message) + " ")
                sys.stdout.flush()
                # we don't have a puppet master here
                # so we need to poll
                if run("which puppet").succeeded:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    break
                message = message + white('.')
                time.sleep(2)

    # this AMI does not let you log in as root.
    # we need to be sure the agent-forwarding is active
    # when we provision, so we pass -E on top of the default
    # fabric sudo prefix. The default rackspace images
    # allow you to ssh as root
    sudo_prefix = "sudo -S -E -p '%(sudo_prompt)s' " % env
    with settings(sudo_prefix=sudo_prefix):
        sudo("puppet apply --modulepath '/home/ubuntu/configuration/modules' /home/ubuntu/configuration/site.pp")
