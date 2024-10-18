import boto3
import json
from utils.logger import Logger
from utils.helpers import decode_url

logger = Logger.get_logger()

DEFAULT_MODEL_ID = 'meta.llama3-1-8b-instruct-v1:0'
DEFAULT_REGION = 'us-west-2'

class BedRockClient:
    def send_request_to_client(self, prompt, model, region):
        formattedPrompt = f"""
            <|begin_of_text|>
            <|start_header_id|>user<|end_header_id|>
            {prompt}
            <|eot_id|>
            <|start_header_id|>assistant<|end_header_id|>
            """
        body = {
            "prompt": formattedPrompt,
            "top_p":0.9,
            "max_gen_len": 200,
            "temperature": 0.5,
        }
        body = json.dumps(body)
        logger.info(f'using model: {model}')
        try:
            client = boto3.client(service_name='bedrock-runtime', region_name=region)
            response = client.invoke_model(body=body, modelId=model, accept="application/json", contentType='application/json')
            response_body = json.loads(response['body'].read())
            generated_text = response_body['generation']
            return generated_text.strip()
        except Exception as e:
            logger.error(f'Error invoking model: {e}')
            raise

    def translate_text(self, text, source_language, target_language, extra_params):
        try:
            model = DEFAULT_MODEL_ID
            region = DEFAULT_REGION
            if extra_params:
                if 'model_id' in extra_params:
                    model = decode_url(extra_params['model_id'])
                if 'region' in extra_params:
                    region = extra_params['region']
            
            prompt = f"""Please translate this text: {text} from language {source_language} to language 
            {target_language} and return only the translated string 
            please nothing else no code no other words"""
            return self.send_request_to_client(prompt, model, region)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def custom_prompt(self, prompt, model, region):
        try:
            return self.send_request_to_client(prompt, model, region)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
        

