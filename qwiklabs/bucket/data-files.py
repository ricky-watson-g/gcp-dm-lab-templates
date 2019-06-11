"""Copies all the data files to student bucket"""


def GenerateConfig(context):
  """Copies all the data files to student bucket"""

  folders = ['cumulus','cumulonimbus','cirrus']

  resources = []

  for x in range(1,21):
    for y in range(0,3):
        resources.append(
            {
                'name': '{}/{}.jpg'.format(folders[y],x),
                'action': 'gcp-types/storage-v1:storage.objects.copy',
                'metadata': {
                    'runtimePolicy': [
                        'CREATE'
                    ],
                    'dependsOn': [
                        context.env['project']
                    ]
                },
                'properties':{
                    'sourceBucket': 'automl-codelab-clouds',
                    'sourceObject': '{}/{}.jpg'.format(folders[y],x),
                    'destinationBucket': context.env['project'],
                    'destinationObject': '{}/{}.jpg'.format(folders[y],x)
                }
            }
        )
        resources.append(
            {
                'name': '{}/{}.jpg-acl'.format(folders[y],x),
                'action': 'gcp-types/storage-v1:storage.objectAccessControls.insert',
                'metadata': {
                    'dependsOn': [
                        '{}/{}.jpg'.format(folders[y],x)
                    ]
                },
                'properties':{
                    'entity': 'allUsers',
                    'role': 'READER',
                    'bucket': context.env['project'],
                    'object': '{}/{}.jpg'.format(folders[y],x)
                }
            }
        )
  return {'resources': resources}
