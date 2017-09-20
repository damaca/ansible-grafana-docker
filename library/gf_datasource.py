#!/usr/bin/python
#coding: utf-8 -*-
import sys, os
import ipaddress
from grafana_api_client import GrafanaClient


DOCUMENTATION = '''
---
module: gf_datasources
short_description: Create/Delete datasources
version_added: "2.3"
author: "@damaca"
description:
   - Create/delete datasources in Grafana
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     required: false
     default: present
   name:
     description:
        - datasource name
     required: true
   org:
     description:
        - Organization where the user below or will be created
     required: true
   type:
     description:
        - datasource type 
     choices: ['elasticsearch', 'cloudwatch', 'influxdb', 'mysql', 'opentsdb', 'prometheus', 'graphite']
     required: true
   url:
     description:
        - Url from the bbdd
     required: true
   database:
     description:
        - database (index) name
     required: true
   basicauth:
     description:
        - enable basic auth
     required: false
     default: false
   user:
     description:
        - Database user
     required: false
   password:
     description:
        - Database password
     required: false
   isdefault:
     description:
        - Is default datasource
     required: false
     default: false
   access:
     description:
        - direct/proxy
     choices: ['direct', 'proxy']
     required: false
     default: proxy
   jsondata:
     description:
        - Extra parameters
     required: false
     default: {}
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
        org=dict(required=True),
        url=dict(required=True),
        type=dict(required=True, choices=['elasticsearch', 'cloudwatch', 'influxdb', 'mysql', 'opentsdb', 'prometheus', 'graphite']),
        database=dict(required=True),
        basicauth=dict(default=False,type='bool'),
        isdefault=dict(default=False,type='bool'),
        access=dict(default='proxy', choices=['direct', 'proxy']),
        user=dict(default=''),
        password=dict(default='',no_log=True),
        jsondata=dict(default={},type='raw'),
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
    datasource_name = module.params['name']
    org_name = module.params['org']
    url = module.params['url']
    ds_type = module.params['type']
    database = module.params['database']
    basicauth = module.params['basicauth']
    isdefault = module.params['isdefault']
    user = module.params['user']
    password = module.params['password']
    access = module.params['access']
    jsondata = module.params['jsondata']
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
    
    g_datasources = client.datasources() 

    curr_ds = None

    for ds in g_datasources:
      if datasource_name == ds['name']:
        curr_ds = ds

    if state == 'present':
      if curr_ds == None:
        ds_created = client.datasources.create(name=datasource_name,type=ds_type,user=user,password=password,url=url,orgid=orgs[0]['id'],database=database,basicauth=basicauth,access=access,jsondata=jsondata)
        module.exit_json(changed=True,id=ds_created['id'],name=datasource_name)
      else:
        module.exit_json(changed=False,id=curr_ds['id'],name=datasource_name)
    elif state == 'absent':
      if user != None:
        client.datasources.delete(name=datasource_name)
        module.exit_json(changed=True,id=user['userId'],name=datasource_name)
      else:
        module.exit_json(changed=False)


# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
