
{#
Copyright 2016 Google Inc. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#}

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
