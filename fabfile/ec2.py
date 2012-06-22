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
from boto.ec2.connection import EC2Connection


@task
def create_server():
    print(green("\nCreating instance Ubuntu 12.04 LTS (micro)\n", bold=True))

def create_instance(ami=""):
    conn = EC2Connection()
    reservation = conn.run_instances(ami, instance_type='m1.large', key_name='ec2-keypair', placement='us-east-1a', block_device_map = mapping)
