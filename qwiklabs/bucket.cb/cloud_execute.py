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
                  'name': 'gcr.io/cloud-builders/gsutil',
                  'args':
                  [
                      'cp',
                      'gs://cloud-training/gcpml/c8/cirrus.jpg', 
                      'gs://%s' % (ctx.env['project'])
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gsutil',
                  'args':
                  [
                      '-m', 
                      'cp', 
                      '-r', 
                      'gs://automl-codelab-clouds/*', 
                      'gs://%s' % (ctx.env['project'])
                  ]
              },
              {
                  'name': 'gcr.io/cloud-builders/gsutil',
                  'args':
                  [
                      'cp',
                      'gs://automl-codelab-metadata/data.csv', 
                      './files/data.csv'
                  ],
                  'volumes': volumes
              },
              {
                 'name': 'ubuntu',
                  'args': [
                      'bash', 
                      '-c', 
                      'sed -i -e "s/placeholder/%s/g" ./files/data.csv' % (ctx.env['project'])
                  ],
                  'volumes': volumes
              },
              {
                  'name': 'gcr.io/cloud-builders/gsutil',
                  'args':
                  [
                      'cp',
                      './files/data.csv',
                      'gs://%s/data.csv' % (ctx.env['project'])
                  ],
                  'volumes': volumes
              }
          ],
          'timeout':
              '120s'
      }
  })

  return {
      'resources': resources
  }