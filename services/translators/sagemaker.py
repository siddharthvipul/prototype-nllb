import boto3
import json
from utils.logger import Logger

logger = Logger.get_logger()

class SageMakerClient:
    def __init__(self) -> None:
        self.client = boto3.client(service_name='runtime.sagemaker', region_name='eu-north-1')
        self.translation_endpoint = ''
        
    def send_request_to_client(self, prompt):
        try:
            data = {
              "inputs": "the mesmerizing performances of the leads keep the film grounded and keep the audience riveted .",
            }
            params = {"return_full_text": True,
            #           "temperature": temp,
                      "min_length": 50,
                      "max_length": 100,
                      "do_sample": True,
            #           "repetition_penalty": rep_penalty,
                      "top_k": 20,
                      }

            payload = {"inputs": "the mesmerizing performances of the leads keep the film grounded and keep the audience riveted .", "parameters": params}

            payload = {}
            response = self.client.invoke_endpoint(EndpointName=self.translation_endpoint,
                                           ContentType='text/csv',
                                           Body=payload)
            print(response)
            result = json.loads(response['Body'].read().decode())
            print(result)
            pred = int(result['predictions'][0]['score'])
            predicted_label = 'M' if pred == 1 else 'B'
            return predicted_label
        except Exception as e:
            logger.error(f'Error invoking model: {e}')
            raise

    def translate_text(self, text, source_language, target_language, extra_params={}):
        try:
            prompt = f"""Please translate this text: {text} from language {source_language} to language 
            {target_language} and return only the translated string 
            please nothing else no code no other words"""
            return self.send_request_to_client(prompt)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def custom_prompt(self, prompt):
        try:
            return self.send_request_to_client(prompt)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
        

