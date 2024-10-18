from services.translators.bedrock import BedRockClient
from services.translators.sagemaker import SageMakerClient
from services.translators.mock import MockTranslationClient

from services.object_store.S3Client import S3Client

'''
Get client for translation and object store (for files)
To add more implementations simply add your implementation here.
The implementations should follow the base api.
'''

def get_translation_client(type='bedrock'):
    if type == 'bedrock':
        return BedRockClient()
    elif type == 'sagemaker':
        return SageMakerClient()
    elif type == 'test':
        return MockTranslationClient()
    
    return BedRockClient() # default client for now


def get_object_store_client(type='s3'):
    if type == 's3':
        return S3Client()
    return S3Client() # default client for now
