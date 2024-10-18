from utils.logger import Logger
from io import BytesIO
import fitz
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = Logger.get_logger()

class TranslatePdfClient:
    def process_block(self, block):
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    font_properties = {"size": span["size"], "color": "#%06x" % span["color"], "font-family": '%s' % span["font"]}
                    if span["text"].strip():
                        bbox = span["bbox"]
                        if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                            bbox = [float(coord) for coord in bbox]
                            if span["text"]:
                                return {
                                    "text": span["text"],
                                    "bbox": bbox,
                                    "font_properties": font_properties
                                }
        return None
        
    def extract_text_blocks(self, doc):
        pages_blocks = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
    
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_block = [executor.submit(self.process_block, block) for block in blocks]
                
                page_blocks = []
                for future in as_completed(future_to_block):
                    block_result = future.result()
                    if block_result:
                        page_blocks.append(block_result)

            pages_blocks.append(page_blocks)
            
        return pages_blocks
        
    def convert_pdf_font_size_to_html(self, pdf_font_size_pt):
        dpi = 96  # Standard screen DPI
        html_font_size_px = (pdf_font_size_pt * dpi) / 72
        return html_font_size_px
   
    def extract_text_blocks_1(self, doc):
        pages_blocks = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]
            page_blocks = []
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_properties = {"size": span["size"], "color": "#%06x" % span["color"], "font-family": '%s' % span["font"]}
                            if span["text"].strip():
                                bbox = span["bbox"]
                                if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                                    bbox = [float(coord) for coord in bbox]
                                    if span["text"]:
                                        page_blocks.append({
                                            "text": span["text"],
                                            "bbox": bbox,
                                            "font_properties": font_properties
                                        })
            pages_blocks.append(page_blocks)
        return pages_blocks   
    
    def translate(self, file, translate_file_text_function, scale):
        if scale is None or scale < 0 or scale > 1:
            logger.debug(f'invalid scale value. Value should be between 0 and 1. Using default 0.5')
            scale = 0.5
        try:
            doc = fitz.open(stream=file, filetype="pdf")
            pages_blocks = self.extract_text_blocks_1(doc)
            
            count_rc = 0
            for page_num, page_blocks in enumerate(pages_blocks):
                page = doc.load_page(page_num)
                for block in page_blocks:
                    text = block["text"]
                    bbox = block["bbox"]
                    font_properties = block["font_properties"]
                    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                        try:
                            if any(c.isalpha() for c in text):
                                translated_text = translate_file_text_function(text)
                                if translated_text:
                                    rect = fitz.Rect(bbox)
                                    page.add_redact_annot(rect, text="")
                                    page.apply_redactions()
                                    adjusted_size = font_properties['size'] - 2 
                                    adjusted_size = "%g" % adjusted_size
                                    html = f'''
                                            <div style="font-size:{adjusted_size}px; font-family:{font_properties["font-family"]}; color:{font_properties["color"]}; overflow:visible;">
                                                {translated_text}
                                            </div>
                                            '''  
                                    rc = page.insert_htmlbox(rect, html, scale_low=scale)
                                    if rc[0] == -1:
                                        count_rc +=1
                                else:
                                    logger.error(f'could not translate text {text}')
                            else:
                                logger.debug(f'No need to translate non-alpha text: {text}')
                        except Exception as e:
                            logger.error(f"Error processing block: '{text}' with bbox: {bbox}")
                            logger.error(e)
                            raise
                    else:
                        logger.error(f"Invalid bbox: {bbox}")
            
            if count_rc > 5:
                logger.error(f'Could not fit multiple lines after translation due to increase in text length. Try scaling down more using the scale argument.')
            
            pdf_bytes = BytesIO()
            doc.save(pdf_bytes, garbage=4, clean=True, deflate=True, deflate_images=True, deflate_fonts=True)
            doc.close()
            pdf_bytes.seek(0)
            return pdf_bytes
        except Exception as e:
            logger.error(fitz.TOOLS.mupdf_warnings())
            logger.error(f"Error processing block: {str(e)}")
            logger.error(e)

