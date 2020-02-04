import base64
import hashlib
from io import BytesIO
import zipfile

in_memory_output_file = BytesIO()
zip_file = zipfile.ZipFile(in_memory_output_file, mode='w', compression=zipfile.ZIP_DEFLATED)
main = """
import os
from pprint import pprint
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import time
credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

def main(request):
    response = 'success'
    project = os.environ.get('GCP_PROJECT')
    networks_request = service.networks().list(project=project)
    networks = networks_request.execute()   
    for network in networks['items']:
        # TODO: Change code below to process each `network` resource:
        if network['name'] == 'default':
            # get firewall rules
            firewall_rules_request = service.firewalls().list(project=project)
            firewall_rules_response = firewall_rules_request.execute()
            if firewall_rules_response.get('items'):
                for firewall in firewall_rules_response.get('items'):
                    if firewall['network'].endswith('/default'):
                        pprint(firewall)
                        firewall_delete_request = service.firewalls().delete(project=project, firewall=firewall['name'])
                        firewall_delete_response = firewall_delete_request.execute()
            
            network_delete_request = service.networks().delete(project=project, network=network['name'])
            network_delete_response = network_delete_request.execute()   
            waiting = True
            while waiting == True:
                waiting = False
                networks_request = service.networks().list(project=project)
                networks = networks_request.execute()   
                for network in networks['items']:
                    if network['name'] == 'default':
                        time.sleep(30)
                        waiting = True
    return response
"""
res = """
# Function dependencies, for example:
# package>=version
google-api-python-client
oauth2client
pprint
"""
zip_file.writestr('main.py', main)
zip_file.writestr('requirements.txt', res)
zip_file.close()
base64.b64encode(in_memory_output_file.getvalue())