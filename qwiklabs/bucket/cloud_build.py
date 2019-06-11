"""Cloud Function (nicely deployed in deployment) DM template."""

import base64
import hashlib
from StringIO import StringIO
import zipfile


def GenerateConfig(ctx):
  """Generate YAML resource configuration."""
  in_memory_output_file = StringIO()
  function_name = ctx.env['deployment'] + 'cf'
  zip_file = zipfile.ZipFile(
      in_memory_output_file, mode='w', compression=zipfile.ZIP_DEFLATED)
  for imp in ctx.imports:
    if imp.startswith(ctx.properties['codeLocation']):
      zip_file.writestr(imp[len(ctx.properties['codeLocation']):],
                        ctx.imports[imp])
  zip_file.close()
  # content = base64.b64encode(in_memory_output_file.getvalue())
  content = "UEsDBBQACAAIAF1wTk4AAAAAAAAAAAAAAAAQABAAcmVxdWlyZW1lbnRzLnR4dFVYDACtJWVckgRlXOmrU18Nyk0KgCAQBtC9pxhwmxcIatk9ZPwS0WbEn+j4uX7P0jWFR1KhgAoJEE7oG93aCJ9/asFuLFXP2Uecx4vW1zZRNRY4LjqD60PbUvMDUEsHCDxc5VBMAAAATgAAAFBLAwQUAAgACAB3fE5OAAAAAAAAAAAAAAAABwAQAG1haW4ucHlVWAwArSVlXFIaZVzpq1NfbVNLa9wwEL77Vwzbg2xqlKa9BXJaSqBQupTe0mBkeezVRta4eqQJIf+9ki1nnbbCoJn5ZkbfPNxbGmEgGjRyqSl0oMaJrAfnyYoBi6ySK4qiwx5GoUxp8VdA56urAuLZ7XbzvbcoPDoQ0CuNoEyU2iDv0cNv5Y/gjwiSjEfjHbgJpeqVBE8zkB2VkTp02PE1c7pmOeVsjBgRroF1wgsu3QNbINIdWheBWybDGHRwrF4kMmpsF1VZG4W7OUIrg8mfLQmWx5fs0UqOo3lQlgwf0JfsZn9oDt+/ffm8/8FqYGgtWVbNke/iWQS4ifTPlbxFczcbqVWsPj6RDXw/G8pqQ+OMZvdEolmwcsM0E8izaE6OTAzN6hyTTGW1NnBD9au4x+043uI9WXhK47PCDFh+qD/lQa/g4xm8rD9ebtC1t6m1g7u6uHh+WT5+mob6+eWnYTxmGMVaCU+V1HmAt0939eNGqf7J6+D99Sz8XdEhuOO6StSeUKZV+u8oWk1tpJefT1r5ulrVqwcPkybRNX38PxrnrTJDORPYuIyxi80UWq1kHqBFH6zZrlPxB1BLBwjWyR95qwEAAGEDAABQSwECFQMUAAgACABdcE5OPFzlUEwAAABOAAAAEAAMAAAAAAAAAABApIEAAAAAcmVxdWlyZW1lbnRzLnR4dFVYCACtJWVckgRlXFBLAQIVAxQACAAIAHd8Tk7WyR95qwEAAGEDAAAHAAwAAAAAAAAAAECkgZoAAABtYWluLnB5VVgIAK0lZVxSGmVcUEsFBgAAAAACAAIAiwAAAIoCAAAAAA=="
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
          'steps': [{
              'name': 'ubuntu',
              'args': ['bash', '-c', cmd],
              'volumes': volumes,
          }, {
              'name': 'gcr.io/cloud-builders/gsutil',
              'args': ['cp', '/function/function.zip', source_archive_url],
              'volumes': volumes
          }],
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