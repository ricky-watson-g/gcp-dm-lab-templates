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

resources:
- name: labs-firewall-rule
  type: compute.v1.firewall
  properties:
    network: $(ref.{{ properties["network"] }}.selfLink)
    sourceRanges: ["0.0.0.0/0"]
    targetTags: [{{ properties["hosttag"] }} ]
    allowed:
    - IPProtocol: TCP
      ports: ["3000","8080","8181","8282","8383"]
