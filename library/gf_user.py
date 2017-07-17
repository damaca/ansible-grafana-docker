#!/usr/bin/python
#coding: utf-8 -*-
import sys, os
import ipaddress
from grafana_api_client import GrafanaClient


DOCUMENTATION = '''
---
module: gf_users
short_description: Create/Delete users from organizations
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
        - User name
     required: true
   role:
     description:
        - Role of the user in the organization
     choices: ['Viewer', 'Admin', 'Editor', 'Read Only Editor']
     required: false
     default: Viewer
   org:
     description:
        - Organization where the user below or will be created
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
        password=dict(required=True,no_log=True),
        role=dict(default='Viewer', choices=['Viewer', 'Admin', 'Editor', 'Read Only Editor']),
        org=dict(required=True),
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
    user_name = module.params['name']
    org_name = module.params['org']
    role = module.params['role']
    password = module.params['password']
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
    
    global_users = client.users() 
    users = client.orgs[orgs[0]['id']].users() 
   
    user = None
    global_user = None

    for gus in global_users:
      if user_name == gus['login']:
        global_user = gus

    if global_user != None:
      for us in users:
        if user_name == us['login']:
          user = us

    if state == 'present':
      if user == None:
        if global_user == None:
          global_user_created = client.admin.users.create(name=user_name,login=user_name,role=role,password=password)
          user_created = client.orgs[orgs[0]['id']].users.create(loginoremail=user_name,role=role)
          #Delete from main org here which is added by default
          client.orgs[1].users[global_user_created['id']].delete()
          module.exit_json(changed=True,id=global_user_created['id'],name=user_name)
        else:
          #The user was in global users before, we need just to add to the org
          client.orgs[orgs[0]['id']].users.create(loginoremail=user_name,role=role)
          module.exit_json(changed=True,id=global_user['id'],name=user_name)
      else:
        module.exit_json(changed=False,id=user['userId'],name=user_name)
    elif state == 'absent':
      if user != None:
        client.orgs[orgs[0]['id']].users.delete(login=user_name)
        module.exit_json(changed=True,id=user['userId'],name=user_name)
      else:
        module.exit_json(changed=False)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
