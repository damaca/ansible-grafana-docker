#!/usr/bin/python
#coding: utf-8 -*-
import ipaddress
import requests
import json
from grafana_api_client import GrafanaClientError
from grafana_api_client import GrafanaClient
import logging

logging.basicConfig(filename="/tmp/test.txt", level=logging.INFO)


DOCUMENTATION = '''
---
module: gf_notifications
short_description: Create/Delete alert notifications
version_added: "2.3"
author: "@damaca"
description:
   - Create/delete alert notifications in Grafana
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     required: false
     default: present
   name:
     description:
        - alert notification name
     required: true
   org:
     description:
        - Organization where the alert notification will be created
     required: true
   settings:
     description:
        - Extra settings
     required: false
     default: {}
   type:
     description:
        - type of alert notification ['email','slack','telegram']
     required: false
     default: False
   gf_user:
     description:
        - Grafana api user name
     required: false
     default: admin
   gf_password:
     description:
        - Grafana api password
     required: false
     default: admin
   gf_host:
     description:
        - Grafana host
     required: false
     default: 127.0.0.1
   gf_port:
     description:
        - Grafana port
     required: false
     default: 3000
requirements:
    - "python >= 2.6"
    - "grafana_api_client"
    - "requests"
'''

EXAMPLES = '''
# Create a new (or update an existing) dashboard
- gf_notifications:
    state: present
    name: My org
'''

def main():
    argument_spec = dict(
        name=dict(required=True),
        org=dict(required=True),
        settings=dict(default={},type='raw'),
        state=dict(default='present', choices=['absent', 'present']),
        notification_type=dict(required=True,  choices=['email','slack','telegram']),
        isdefault=dict(default=True,type='bool'),
        gf_user=dict(default='admin'),
        gf_password=dict(default='admin',no_log=True),
        gf_host=dict(default='127.0.0.1'),
        gf_port=dict(default=3000,type='int'),
    )

    required_if = [
        
    ]

    mutually_exclusive = []

    module = AnsibleModule(argument_spec, required_if=required_if, mutually_exclusive=mutually_exclusive,
                           supports_check_mode=True)
    
    state = module.params['state']
    ntf_name = module.params['name']
    org_name = module.params['org']
    ntf_type= module.params['notification_type']
    isdefault = module.params['isdefault']
    settings = module.params['settings']
    gf_user = module.params['gf_user']
    gf_password = module.params['gf_password']
    gf_host = module.params['gf_host']
    gf_port = module.params['gf_port']

    if not ipaddress.ip_address(unicode(gf_host)):
      module.fail_json(msg='The host parameter is not a valid ip address.')

    client = GrafanaClient((gf_user, gf_password), host=gf_host, port=gf_port)

    orgs = client.orgs(name=org_name)

    if not len(orgs) > 0:
      module.fail_json(msg='The organization '+org_name+' does not exist.')

    #Change user context to the desired org
    client.user.using[orgs[0]['id']].create()

    url_base = 'http://'+gf_host+':'+str(gf_port)+'/api/alert-notifications'
    
    ntf = None
    ntfr = requests.get(url_base, auth=(gf_user,gf_password), headers={'Content-Type': 'application/json'})
    
    for nt in ntfr.json():
      if ntf_name == nt['name']:
        ntf = nt


    if state == 'present':
      if ntf == None:
        body = { 'name': ntf_name, 'type': ntf_type, 'isDefault': isdefault, 'settings': settings }
        ntf_createdr = requests.post(url_base, auth=(gf_user,gf_password), headers={'Content-Type': 'application/json'}, data=json.dumps(body))
        ntf_created = ntf_createdr.json() 
        logging.info(ntf_createdr.text)
        module.exit_json(changed=True,notifications_id=ntf_created['id'])
      else:
        module.exit_json(changed=False,notifications_id=ntf['id'])
    elif state == 'absent':
      if ntf != None:
        requests.delete(url_base+'/'+ntf['id'], auth=(gf_user,gf_password), headers={'Content-Type': 'application/json'})
        module.exit_json(changed=True)
      else:
        module.exit_json(changed=False)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
