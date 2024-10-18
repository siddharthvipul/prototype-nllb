from utils.logger import Logger
import json

logger = Logger.get_logger()

class ObjectStoreClient:
    def __init__(self) -> None:
        self.client = client
          
    def create_url(self, file_name, client_action):
        url = self.create_url(file_name, client_action)
        return url
    
    def upload_file(self, url, file):
        try:
            self.client.upload_file(url, file)
        except FileNotFoundError:
            logger.error(
                f"Couldn't find {url} For a PUT operation, the key must be the "
                f"name of a file that exists on your computer."
            )
            raise

    def get_file(self, url):
        try:
            return self.client.get_file(url)
        except:
            logger.error(f'Could not get file. {url}')
            raise
    
    def delete_file(self, file_name):
        try:
            return self.client.delete_file(file_name)
        except Exception as e:
            logger.error(f'Could not remove file. {file_name}, {str(e)}')
            return {
                    'statusCode': 400,
                    'body': json.dumps(str(e))
                }