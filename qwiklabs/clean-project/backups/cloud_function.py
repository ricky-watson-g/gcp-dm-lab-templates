"""Cloud Function (nicely deployed in deployment) DM template."""

import base64
import hashlib
from io import BytesIO
import zipfile

def GenerateConfig(ctx):
  """Generate YAML resource configuration."""
  in_memory_output_file = BytesIO()
  function_name = ctx.env['deployment'] + 'cf'
  zip_file = zipfile.ZipFile(
      in_memory_output_file, mode='w', compression=zipfile.ZIP_DEFLATED)
  for imp in ctx.imports:
    if imp.startswith(ctx.properties['codeLocation']):
      zip_file.writestr(imp[len(ctx.properties['codeLocation']):],
                        ctx.imports[imp])
  zip_file.close()
  content = base64.b64encode(in_memory_output_file.getvalue())
  ## the code above doesnt work inside DM, run at outside to create the encoded zip
  content = "UEsDBBQAAAAIAAa3J1BriUpQJQIAAPIGAAAHAAAAbWFpbi5weZ1VS2+cMBC+8yss9WCQIvq6ReK0bSP1slG1t2i1ccwA0xqb2mZp/30N5r1LmsQHHp5vvpn5xgwBlpXSligTZFqVpKo0Skv6Xf/mLblSuQBWIRcIEyRFw9UZ9F+PUqy2xScPiZfIu45gpyF1m8iECXqDxRICPu2T5BIb52BPrKoEcmZRyVMKGauFDaPAgD4jB+c15hI/1SjSkHJVVrUFekPo+aO7zoIks+coCBwdKRnKUMPvGoyNbgPilgZTKWlacmpqzsEY2hkqrX4Ct25fmRjkGbWSbY4hvdvdn+5/7L9/3R1o1GEl2EbpX+bUczunPud4MIVRLNDYsKdN+vvS3/mtqWL4A9xVGEYO14EzpQcUQTk6PFC0UBp69HW16x057L/sb8muYDIHwlUK5AmEaohVbX1tsQQYL8hjz/LY6qFqzWFiwWyI8UAlK4EeSeLE6ttDJ6AP6SQiGWpomBBE1wLMAjCYTp3pimAD4HnFNunGbl4PNMm5oHE1bjD5lntpo2WtQzPGal033saySsHp7AWnR3fyUtOgLUL6flB8g6A7tN3nHA5E0SZwzDMFARb+0wcPWnfiZmRJZpl3J+Q1gS87tsxpo2WLl16v7Wpmn+FWMT0kWR326PlAY/bXU1gl310ahhZl7nwOuga/VaCAyeAtU5snj29umEGwyubNc2fO8aLZ03XwxfOnXa+aHu1q/xWxEQBV+PnD5Tm6Ip4GW2s5TvLgH1BLAwQUAAAACAAGtydQVibogV0AAABnAAAAEAAAAHJlcXVpcmVtZW50cy50eHQtyjEKhDAQRuE+pxiwNY2lsJZ7jyH+xmGzM0OMorfXwurxwQsdfXdNTUxphkNnaBJsPS1WCSf/vWAMHTmnH2dMnwN1e+6QzXJBZJfoV1tNYyoCbcF4b+vwwr3KkxtQSwECFAMUAAAACAAGtydQa4lKUCUCAADyBgAABwAAAAAAAAAAAAAAgAEAAAAAbWFpbi5weVBLAQIUAxQAAAAIAAa3J1BWJuiBXQAAAGcAAAAQAAAAAAAAAAAAAACAAUoCAAByZXF1aXJlbWVudHMudHh0UEsFBgAAAAACAAIAcwAAANUCAAAAAA=="
  m = hashlib.md5()
  m.update(content)
  source_archive_url = 'gs://%s/%s' % (ctx.properties['codeBucket'],
                                       m.hexdigest() + '.zip')
  cmd = "echo '%s' | base64 -d > /function/function.zip;" % (content)
  volumes = [{'name': 'function-code', 'path': '/function'}]
  build_step = {
      'name': 'upload-function-code',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
          'runtimePolicy': ['UPDATE_ON_CHANGE']
      },
      'properties': {
          'steps': [
              {
                'name': 'ubuntu',
                'args': ['bash', '-c', cmd],
                'volumes': volumes,
              },
              {
                'name': 'gcr.io/cloud-builders/gsutil',
                'args': ['cp', '/function/function.zip', source_archive_url],
                'volumes': volumes
              },
              {
                'name': 'gcr.io/cloud-builders/gsutil',
                'args': ['acl', 'ch', '-u', 'AllUsers:R', source_archive_url],
                'volumes': volumes
              }
          ],
          'timeout':
              '120s'
      }
  }
  cloud_function = {
      'type': 'gcp-types/cloudfunctions-v1:projects.locations.functions',
      'name': function_name,
      'properties': {
          'parent':
              '/'.join([
                  'projects', ctx.env['project'], 'locations',
                  ctx.properties['location']
              ]),
          'function':
              function_name,
          'labels': {
              # Add the hash of the contents to trigger an update if the bucket
              # object changes
              'content-md5': m.hexdigest()
          },
          'sourceArchiveUrl':
              source_archive_url,
          'environmentVariables': {
              'codeHash': m.hexdigest()
          },
          'entryPoint':
              ctx.properties['entryPoint'],
          'httpsTrigger': {},
          'timeout':
              ctx.properties['timeout'],
          'availableMemoryMb':
              ctx.properties['availableMemoryMb'],
          'runtime':
              ctx.properties['runtime']
      },
      'metadata': {
          'dependsOn': ['upload-function-code']
      }
  }
  resources = [build_step, cloud_function]

  return {
      'resources':
          resources,
      'outputs': [{
          'name': 'sourceArchiveUrl',
          'value': source_archive_url
      }, {
          'name': 'name',
          'value': '$(ref.' + function_name + '.name)'
      }]
  }