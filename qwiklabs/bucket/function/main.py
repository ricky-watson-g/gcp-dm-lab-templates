from google.cloud import storage
import os


def main(request):
    """
    Creates a file in a bucket with the contents specific to the bucket included.
    """    
    file_name = 'data.csv'
    folders = ['cumulus','cumulonimbus','cirrus']
    lines = ''
    bucket_name  = os.environ.get('GCP_PROJECT', 'error')
    ####
    # Get the bucket
    ####
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    #request_json = request.get_json()   
    ####
    # Make the content
    ####
    for y in range(0,3):
        for x in range(1,21):
            line = 'gs://{}/{}/{}.jpg,{}\n'.format(bucket.name,folders[y],x,folders[y])
            lines += line
    ####
    # Push to the object in bucket
    ####
    blob = bucket.blob(file_name)
    blob.upload_from_string(lines)
    blob.make_public()
    return bucket_name
