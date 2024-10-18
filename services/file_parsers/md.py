from utils.logger import Logger
from io import BytesIO
from mistletoe.block_token import BlockToken, Heading, Paragraph, SetextHeading
from mistletoe.span_token import InlineCode, RawText, SpanToken
import mistletoe
from mistletoe.markdown_renderer import MarkdownRenderer

logger = Logger.get_logger()

class TranslateMdClient:
    def update_text(self, token: SpanToken, translate_file_text_function):
        if isinstance(token, RawText):
            translated_text = translate_file_text_function(token.content)
            if translated_text:
                token.content = translated_text

        if not isinstance(token, InlineCode) and hasattr(token, "children"):
            if token.children:
                for child in token.children:
                    self.update_text(child, translate_file_text_function)

    def update_block(self, token: BlockToken, translate_file_text_function):
        if token.children is None:
            return
        
        if token.children is not None:
            if isinstance(token, (Paragraph, SetextHeading, Heading)):
                for child in token.children:
                    self.update_text(child, translate_file_text_function)

            for child in token.children:
                if isinstance(child, BlockToken):
                    self.update_block(child, translate_file_text_function)

        
    def translate(self, file, translate_file_text_function):
        try:
            with MarkdownRenderer() as renderer:
                lines_array = file.readlines()
                lines_array = [line.decode('utf-8') for line in lines_array]

                document = mistletoe.Document(lines_array)
                self.update_block(document, translate_file_text_function)
                md = renderer.render(document)

                md_bytes = BytesIO()
                md_bytes.write(md.encode('utf-8'))
                md_bytes.seek(0)
                return md_bytes
        except Exception as e:
            logger.error(f"Error processing block: {str(e)}")
            logger.error(e)

