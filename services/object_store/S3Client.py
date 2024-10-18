from utils.logger import Logger
import boto3
from botocore.exceptions import ClientError
import requests
import io
import json
import os
from dotenv import load_dotenv

load_dotenv()

logger = Logger.get_logger()

BUCKET_NAME = os.environ["BUCKET_NAME"]
BUCKET_REGION = os.environ["BUCKET_REGION"]

class S3Client:
    def __init__(self) -> None:
        self.client = boto3.client(service_name='s3', region_name=BUCKET_REGION)
        
    def generate_presigned_url(self, client_method, method_parameters, expires_in):
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=client_method, Params=method_parameters, ExpiresIn=expires_in
            )
            logger.info("Got presigned URL: %s", url)
            return url
        except ClientError:
            logger.exception(
                "Couldn't get a presigned URL for client method '%s'.", client_method
            )
            raise
        
    def create_url(self, file_name, client_action):
        url = self.generate_presigned_url(client_action, {"Bucket": BUCKET_NAME, "Key": file_name}, 30000)
        return url
    
    def upload_file(self, url, file):
        try:
            response = requests.put(url, data=file)
            logger.debug(f"response:  {response.reason}, {response.status_code}")
        except FileNotFoundError:
            logger.error(
                f"Couldn't find {url} For a PUT operation, the key must be the "
                f"name of a file that exists on your computer."
            )
            raise

    def get_file(self, url):
        try:
            object_in_s3 = requests.get(url)
            object_as_file_like = io.BytesIO(object_in_s3.content)
            return object_as_file_like
        except:
            logger.error(f'Could not get file. {url}')
            raise
    
    def delete_file(self, file_name):
        try:
            self.client.delete_object(
                    Bucket=BUCKET_NAME,
                    Key=file_name,
                )
            return json.dumps({'success':True})
        except Exception as e:
            logger.error(f'Could not remove file. {file_name}, {str(e)}')
            raise