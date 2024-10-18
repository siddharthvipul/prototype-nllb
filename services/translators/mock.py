from utils.logger import Logger
from deep_translator import GoogleTranslator

logger = Logger.get_logger()

class MockTranslationClient:
    def translate_text(self, text, source_language, target_language, extra_params={}):
        try:
            translator = GoogleTranslator(source=source_language, target=target_language)
            translated_text = translator.translate(text)
            return translated_text
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
    
    def custom_prompt(self, prompt):
        try:
            return prompt
        except Exception as e:
            logger.error(f'Error in translate: {e}')
            raise
        

