import os
import time
import sys
from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError
from pycloud.utils.spinner import Spinner
from pycloud.utils.console import Console
from pycloud.utils.colors import green
from pycloud.utils.colors import magenta
from pycloud.utils.colors import red
from pycloud.utils.colors import white
from pycloud.models.cloudservers import CloudServer

# key_pair_name = 'id_rsa.pub'
# placement = 'us-east-1a'
# instance_type = 't1.micro'
# ami = 'ami-a29943cb' # ubuntu 12.04

class EC2(object):

    def create(self, image_id, type_id, **kwargs):
        spinner = Spinner()
        console = Console()

        sleep_time = 0.200
        sleep_index = 0;
        tags = None

        if "tags" in kwargs:
            tags = kwargs['tags']
            del kwargs['tags']

        console.write_ln(white("Validating image id {}".format(image_id), bold=True))

        image = None
        conn = EC2Connection()

        try:
            image = conn.get_image(image_id)
        except EC2ResponseError:
            console.write_ln(red("Invalid image id {}".format(image_id), bold=True))
            return

        console.write_ln(white("Creating instance {} ({})".format(image.name, image.id), bold=True))

        reservation = image.run(instance_type=type_id, **kwargs)

        # reservation = conn.run_instances(image_id,
        #                                  instance_type=type_id,
        #                                  **kwargs)

        instance = reservation.instances[0]

        console.write_ln(magenta('Waiting for instance to start...'))
        # Check up on its status every so often

        status = instance.update()

        while status == 'pending':
            time.sleep(sleep_time)
            sleep_index += sleep_time

            if int(sleep_index) == 10:
                sleep_index = 0
                status = instance.update()

            console.write(magenta("Building ({}) {} ".format(status, white(spinner.next()))))

        if status == 'running':
            console.write(magenta('New instance "' + instance.id + '" accessible at ' + instance.public_dns_name))
        else:
            console.write(red('Instance status: ' + status))
            return

        console.write_ln("")

        server = CloudServer()
        server.dns_name   = instance.public_dns_name
        server.id         = instance.id
        server.ip_address = instance.ip_address

        if tags:
            conn.create_tags([instance.id], tags)

    def get_servers(self, filters=None):
        console = Console()
        console.write_ln(white("Retrieving servers...", bold=True))

        conn = EC2Connection()
        results = []
        try:
            reservations = conn.get_all_instances(filters=filters)
        except EC2ResponseError:
            return results

        for reservation in reservations:
            instance = reservation.instances[0]
            server = CloudServer()
            server.dns_name   = instance.public_dns_name
            server.id         = instance.id
            server.ip_address = instance.ip_address
            results.append(server)

        return results

    def terminate_servers(self, ids):
        console = Console()
        console.write_ln(white("Terminating servers ({})".format(ids), bold=True))

        conn = EC2Connection()
        try:
            conn.terminate_instances(ids)
        except EC2ResponseError:
            pass


