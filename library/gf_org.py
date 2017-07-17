#!/usr/bin/python
#coding: utf-8 -*-
import sys, os
import ipaddress
from grafana_api_client import GrafanaClient


DOCUMENTATION = '''
---
module: gf_org
short_description: Create/Delete organizations in Grafana
version_added: "2.3"
author: "David Martin"
description:
   - Create/delete organizations in Grafana
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     required: false
     default: present
   name:
     description:
        - Org name
     required: true
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
'''

EXAMPLES = '''
# Create a new (or update an existing) organization
- gf_org:
    state: present
    name: My org
'''

def main():
    argument_spec = dict(
        name=dict(required=True),
        state=dict(default='present', choices=['absent', 'present']),
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
    org_name = module.params['name']
    gf_user = module.params['gf_user']
    gf_password = module.params['gf_password']
    gf_host = module.params['gf_host']
    gf_port = module.params['gf_port']

    if not ipaddress.ip_address(unicode(gf_host)):
      module.fail_json(msg='The host parameter is not a valid ip address.')

    client = GrafanaClient((gf_user, gf_password), host=gf_host, port=gf_port)

    orgs = client.orgs(name=org_name)
    if state == 'present':
      if not len(orgs) > 0:
        # The org not exist so I can create
        org_created = client.orgs.create(name=org_name)
        module.exit_json(changed=True,id=org_created['orgId'],name=org_name)
      else:
        # The org exist do nothing
        module.exit_json(changed=False,id=orgs[0]['id'],name=org_name)

    elif state == 'absent':
      if len(orgs) > 0:
        # The org exist so I can delete
        client.orgs.delete(name=org_name)
        module.exit_json(changed=True,id=orgs[0]['id'],name=org_name)
      else:
        module.exit_json(changed=False)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
