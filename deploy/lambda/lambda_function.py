import json
from utils.logger import Logger

logger = Logger(name="NLLB Logger")
logger = Logger.get_logger()

from services.api import ApiClient
from utils.helpers import response_object
from utils.client import get_object_store_client, get_translation_client
from services.translators.bedrock import BedRockClient

from services.file_parsers.docx import TranslateDocxClient
from services.file_parsers.pdf import TranslatePdfClient
from services.file_parsers.md import TranslateMdClient

translation_client = get_translation_client()
object_store_client = get_object_store_client()

pdf_client = TranslatePdfClient()
docx_client = TranslateDocxClient()
md_client = TranslateMdClient()
       
            
def lambda_handler(event, context):
    try:
        action = event["queryStringParameters"]["action"]
        if(not action):
            return response_object(500, 'Action is not defined!')
            
        logger.info(f'Action:  {action}')
        
        apiClient = ApiClient(translation_client=translation_client, object_store_client=object_store_client, pdf_client=pdf_client, docx_client=docx_client, md_client=md_client)
    
        event_body = json.loads(event["body"])
        if action == "health-check":
            logger.info(f'Checking health')
            return apiClient.health_check()
           
        elif action == "translate":
            logger.info(f'translating text')

            text = event_body["text"]
            if(not text or text == ""):
                return response_object(500, 'Text is not given!')
            model_id = event_body["model_id"]
            region = event_body["region"]
            
            source_language =  event_body["source_language"] 
            target_language = event_body["target_language"]
            
            if(not source_language or not target_language):
                return response_object(500, 'Source and target are required!')
            
            if(not model_id or not region):
                translated_text =  apiClient.translate_text(text, source_language, target_language)
            else:
                extra_params = {'model_id': model_id, 'region':region}
                translated_text =  apiClient.translate_text(text, source_language, target_language, extra_params=extra_params)
            return response_object(200, translated_text)
                
        elif action == "get-presigned-url":
            logger.info(f'Get presigned urls') 

            client_action = event_body["client_action"]
            if(not client_action):
                return response_object(500, 'Something went wrong!')
                
            file_name = event_body["name"]
            if(not file_name):
                return response_object(500, 'file name is not given!')
                
            url =  object_store_client.create_url(file_name, client_action)
            return response_object(200, url)
                
        elif action == "translate-file":
            logger.info(f'translating file')

            get_url = event_body["get_url"]
            put_url = event_body["put_url"]
            pdf_scale_down_ratio = event_body["scale"] if "scale" in event_body else None
            original_file_name = event_body["original_file_name"]
            if(not get_url or not put_url):
                return response_object(500, 'file url is not given!')
                
            source_language =  event_body["source_language"] 
            target_language = event_body["target_language"]
            if(not source_language or not target_language):
                return response_object(500, 'Source and target language are required!')
            
            model_id = event_body["model_id"]
            region = event_body["region"]
             
            if(not model_id or not region):
                apiClient.translate_file(get_url, put_url, original_file_name, source_language, target_language, scale=pdf_scale_down_ratio)
            else:
                extra_params = {'model_id': model_id, 'region':region}
                apiClient.translate_file(get_url, put_url, original_file_name, source_language, target_language, scale=pdf_scale_down_ratio, extra_params=extra_params)
            return response_object(200, 'file translated!')
        
        elif action == "delete-file":
            file_name = event_body["name"]
            if(not file_name):
                return response_object(500, 'file name is not given!')
                
            object_store_client.delete_file(file_name)
            return response_object(200, 'file cleared!')
            
        elif action == "custom-prompt":
            logger.info(f'custom-prompt')
            text = event_body["text"]
            result =  apiClient.custom_prompt(text)
            return response_object(200, result)
        
        elif action == "bedrock-custom-prompt":
            logger.info(f'bedrock custom-prompt')
            text = event_body["text"]
            model = event_body["model"]
            region = event_body["region"]
            bedrock_client = BedRockClient()
            result =  bedrock_client.custom_prompt(text, model, region)
            return response_object(200, result)
    
        return response_object(500, 'Action is not correct!')       
        
    except Exception as e:
        logger.error(e)
        return response_object(500, str(e))      