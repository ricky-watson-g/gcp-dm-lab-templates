"""Execute in Cloud Build DM template."""

def GenerateConfig(ctx):
  """Generate YAML resource configuration."""
  volumes = [{'name': 'file-store', 'path': '/files'}]
  resources = []
  resources.append({
      'name': 'upload-function-code',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
          'runtimePolicy': ['UPDATE_ON_CHANGE']
      },
      'properties': {
          'steps': [
              {
                  'name': 'gcr.io/cloud-builders/curl',
                  'args':
                  [
                      'https://api.openweathermap.org/data/2.5/weather?q=Christchurch&appid=30bafffec3cd58ca426e5bcf27c7db27',
                      '-o',
                      'return.txt'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'get-value', 
                      '%s-username' % (ctx.env['deployment']), 
                      '--config-name=lab'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'get-value', 
                      '%s-password' % (ctx.env['deployment']), 
                      '--config-name=lab'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'set', 
                      '%s-username' % (ctx.env['deployment']), 
                      'billyusername', 
                      '--config-name=lab',
                      '--is-text'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'set', 
                      '%s-password' % (ctx.env['deployment']), 
                      'billypassword', 
                      '--config-name=lab',
                      '--is-text'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'get-value', 
                      '%s-username' % (ctx.env['deployment']), 
                      '--config-name=lab'
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gcloud',
                  'args':
                  [
                      'beta', 
                      'runtime-config', 
                      'configs', 
                      'variables', 
                      'get-value', 
                      '%s-password' % (ctx.env['deployment']), 
                      '--config-name=lab'
                  ]
              }
          ],
          'timeout':
              '120s'
      }
  })

  return {
      'resources': resources
  }