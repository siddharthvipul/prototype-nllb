import sys
sys.path.append(".")

from datetime import datetime

from utils.logger import Logger

logger = Logger.get_logger()

class ApiClient:
    def __init__(self, translation_client, object_store_client, docx_client, pdf_client, md_client) -> None:
        self.translation_client = translation_client
        self.object_store_client = object_store_client
        self.docx_client = docx_client
        self.pdf_client = pdf_client
        self.md_client = md_client
    
    def health_check(self):
        now = datetime.now()
        return now.strftime("%m/%d/%Y, %H:%M:%S")
    
    def translate_text(self, text, source_language, target_language, extra_params={}):
        try:
            return self.translation_client.translate_text(text, source_language, target_language, extra_params)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def translate_file(self, get_url, put_url, original_file_name, source_language, target_language, scale=0.5, extra_params={}):
        try:
            if not original_file_name.endswith('.docx') and not original_file_name.endswith('.pdf') and not original_file_name.endswith('.md'):
                raise Exception ("File format not supported")
            
            file_object = self.object_store_client.get_file(get_url)
            translate_file_text_function = self.translate_file_text_function(source_language, target_language, extra_params)
            
            if original_file_name.endswith('.docx'):
                translated_file = self.docx_client.translate(file_object, translate_file_text_function)
            elif original_file_name.endswith('.pdf'):
                translated_file = self.pdf_client.translate(file_object, translate_file_text_function, scale)
            elif original_file_name.endswith('.md'):
                translated_file = self.md_client.translate(file_object, translate_file_text_function)

            self.object_store_client.upload_file(put_url, translated_file)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def custom_prompt(self, prompt, model, region):
        try:
            return self.translation_client.custom_prompt(prompt, model, region)
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def translate_file_text_function(self, source_language, target_language, extra_params):
        def translate_file_text(file_text):
            return self.translation_client.translate_text(file_text, source_language, target_language, extra_params)
        
        return translate_file_text
        
        
        
        

