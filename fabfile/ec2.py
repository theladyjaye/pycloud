import os
import time
import sys
import boto
from boto.ec2.connection import EC2Connection
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

from .utils.spinner import Spinner
from .utils.console import Console


@task
def create_server():
    key_pair_name = 'ec2-blitz'
    placement = 'us-east-1a'
    instance_type = 't1.micro'
    ami = 'ami-a29943cb' # ubuntu 12.04
    
    spinner = Spinner()
    console = Console()

    sleep_time = 0.200
    sleep_index = 0;
    

    console.write_ln(green("\nCreating instance Ubuntu 12.04 LTS (t1.micro)\n", bold=True))

    conn = EC2Connection()
    reservation = conn.run_instances(ami,\
                                     instance_type=instance_type, \
                                     key_name=key_pair_name, \
                                     placement=placement)

    instance = reservation.instances[0]

    console.write_ln('Waiting for instance to start...')
    # Check up on its status every so often
    
    status = instance.update()
    
    while status == 'pending':
        time.sleep(sleep_time)
        sleep_index += sleep_time
        
        if int(sleep_index) == 10:
            sleep_index = 0
            status = instance.update()
        
        console.write("Building ({}) {} ".format(status, spinner.next()))

    if status == 'running':
        console.write('New instance "' + instance.id + '" accessible at ' + instance.public_dns_name)
    else:
        console.write('Instance status: ' + status)
        return

