from fabric.api import task
from pycloud.services.cloudservers import CloudServerService
from pycloud.providers.amazon import EC2

@task
def create():
    service = CloudServerService(provider=EC2())
    service.create(image_id='ami-a29943cb',
                  type_id='t1.micro',
                  key_name='id_rsa.pub',
                  placement='us-east-1a',
                  security_groups=['default', 'webservers'],
                  user_data='',
                  instance_initiated_shutdown_behavior='terminate',
                  tags={'project':'test'})

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

