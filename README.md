Role Name
=========

Simple role to install grafana with docker and create (if exists) some orgs,users and datasources in these orgs. This role is WIP.

Requirements
------------

docker and docker-py installed

Role Variables
--------------

```
       admin_pass: "mypass"
       run_once_post_install: true #When several host modify the same database this should be true
       environment_vars:
         GF_SECURITY_ADMIN_PASSWORD: "{{admin_pass}}"
         GF_SERVER_DOMAIN: "{{ domain }}"
         GF_SERVER_ROOT_URL: "https://{{ domain }}/grafana"
         GF_DATABASE_URL: "mysql://grafana:grafanapass@{{inventory_hostname}:3306/grafana"
       notifications:
         email:
         name: email
         type: email
         settings:
           addresses: "someaddress@any.com"
       datasources:
         filebeat:
           name: filebeat
           url: "http://localhost:9200"
           database: "[filebeat-]YYYY.MM.DD"
           type: elasticsearch
           jsondata:
             esVersion: 5
             interval: "Daily"
             timeField: "@timestamp"
       orgs:
         - name: ops
           users:
             - name: pruebaops
               role: Viewer
               password: prueba
           datasources:
             - "{{datasources.filebeat}}"
           dashboards:
             - { name: "test", file: "files/somefile.json" }
           notifications:
             - "{{notifications.email}}"
         - name: product
           users:
             - name: pruebaprod
               role: Viewer
               password: prueba
           datasources: []
           dashboards: []
           notifications: []

```

Example Playbook
----------------


License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
