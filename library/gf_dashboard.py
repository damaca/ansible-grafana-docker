#!/usr/bin/python
#coding: utf-8 -*-
import ipaddress
from grafana_api_client import GrafanaClientError
from grafana_api_client import GrafanaClient


DOCUMENTATION = '''
---
module: gf_dashboard
short_description: Create/Delete dashboard
version_added: "2.3"
author: "@damaca"
description:
   - Create/delete dashboard in Grafana
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     required: false
     default: present
   name:
     description:
        - dashboard name
     required: true
   org:
     description:
        - Organization where the dashboard will be created
     required: true
   jsondata:
     description:
        - Extra parameters
     required: false
     default: {}
   overwrite:
     description:
        - Overwrite an existing dashboard
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
'''

EXAMPLES = '''
# Create a new (or update an existing) dashboard
- gf_dashboard:
    state: present
    name: My org
'''

def main():
    argument_spec = dict(
        name=dict(required=True),
        org=dict(required=True),
        jsondata=dict(default={},type='raw'),
        state=dict(default='present', choices=['absent', 'present']),
        overwrite=dict(required=False, default=False, type='bool', choices=[True,False]),
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
    dashboard_name = module.params['name']
    org_name = module.params['org']
    overwrite= module.params['overwrite']
    ds_json = module.params['jsondata']
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

    # Changing some values with the parameter values
    ds_json['dashboard']['title'] = dashboard_name 
    ds_json['dashboard']['id'] = 'null'
    ds_json['dashboard']['version'] = 0

    slug = dashboard_name.replace(" ","")
    #Change user context to the desired org
    client.user.using[orgs[0]['id']].create()
    
    try:
      g_dashboard = client.dashboards.db[slug]() 
      # If we get some dashboard and overwrite is True we change the id and increment the version number
      if overwrite:
        ds_json['dashboard']['id'] = g_dashboard['dashboard']['id']
        ds_json['dashboard']['version'] = g_dashboard['dashboard']['version'] + 1 
    except GrafanaClientError as e:
      if '404' in str(e):
        g_dashboard = None

    if state == 'present':
      if g_dashboard == None or overwrite:
        ds_created = client.dashboards.db.create(dashboard=ds_json['dashboard'],overwrite=overwrite)
        module.exit_json(changed=True,slug=ds_created['slug'],version=ds_created['version'])
      else:
        module.exit_json(changed=False,slug=slug, version=g_dashboard['dashboard']['version'])
    elif state == 'absent':
      if g_dashboard != None:
        client.dashboards.db.delete(slug=slug)
        module.exit_json(changed=True)
      else:
        module.exit_json(changed=False)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
