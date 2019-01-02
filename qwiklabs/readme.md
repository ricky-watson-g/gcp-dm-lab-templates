# qwikLABS notes


When you are creating templates for qwikLABS deployments please bear in mind the qwikLABS platform:
1. Expects a qwiklabs resource
2. rewrites the .yaml file to insert variables for the project ID, and the account email and password

Examples provided will work as expected and come in jinja and python forms.

### env and properties

Make sure you are referencing the correct variable store, properties are set in the calling resource section.  machineType, zone, network and hosttag are all used via properties\[\].

#### qwiklabs.jinja section
``` 
{% set NETWORK_NAME = "lab-network" %}
{% set ZONE1 = "us-central1-f" %}
{% set ZONE2 = "us-central1-c" %}
{% set NAME1 = "lab-1" %}
{% set NAME2 = "lab-2" %}
{% set HOST_TAG = "labvm" %}

resources:
- name: {{ NAME1 }}
  type: vm.jinja
  properties:
    machineType: f1-micro
    zone: {{ ZONE1 }}
    network: {{ NETWORK_NAME }}
    hosttag: {{ HOST_TAG }}
```

#### vm.jinja section

```
{% set EMAIL = env['project'] +'@'+ env['project'] +'.iam.gserviceaccount.com' %}

resources:
- type: gcp-types/compute-v1:instances
  name: {{ env["name"] }}
  properties:
    zone: {{ properties["zone"] }}
    machineType: zones/{{ properties["zone"] }}/machineTypes/n1-standard-1
    disks:
    - boot: true
      autoDelete: true
      initializeParams:
        sourceImage: projects/debian-cloud/global/images/family/debian-9
    networkInterfaces:
    - network: $(ref.{{ properties["network"] }}.selfLink)
      accessConfigs:
      - name: External NAT
        type: ONE_TO_ONE_NAT
    serviceAccounts:
      - email: {{ EMAIL }}
        scopes:
        - https://www.googleapis.com/auth/cloud-platform
        - https://www.googleapis.com/auth/source.full_control
    tags:
      items:
        - {{ properties["hosttag"] }}
```

#### Notes 
 - locally decleared variables (in this instance EMAIL) are used inside {{ }} and spacing is important
 - $ref allows you to reference a subvalue
 - env contains values passed down outside outside of the properties, such as name
