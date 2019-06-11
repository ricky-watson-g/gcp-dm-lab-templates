"""Execute in Cloud Build DM template."""

def GenerateConfig(ctx):
  """Generate YAML resource configuration for a qwiklab"""
  resources = []
  resources.append({
      'name': 'provision-lab-environment',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
          'runtimePolicy': ['UPDATE_ON_CHANGE']
      },
      'properties': {
          'steps': [
              {
                 'name': 'gcr.io/community-builders/bq',
                  'args': [
                      'mk', 
                      '--dataset', 
                      '%s:Logs' % (ctx.env['project'])
                  ]
              },
              {
                 'name': 'gcr.io/community-builders/bq',
                  'args': [
                      'mk', 
                      '--table', 
                      '%s:Logs:logs' % (ctx.env['project']),
                      'user_id:integer,ip:string,datetime:datetime,http_request:string,lat:float,long:float,http_response:integer,user_agent:string,num_bytes:integer'
                  ]
              }
          ],
          'timeout':
              '60s'
      }
  })

  return {
      'resources': resources
  }