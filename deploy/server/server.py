import sys
sys.path.append(".")

from utils.logger import Logger

logger = Logger(name="NLLB Logger")
logger = Logger.get_logger()

import nest_asyncio
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

from services.api import ApiClient
from services.translators.bedrock import BedRockClient
from utils.client import get_object_store_client, get_translation_client

from services.file_parsers.docx import TranslateDocxClient
from services.file_parsers.pdf import TranslatePdfClient
from services.file_parsers.md import TranslateMdClient
     
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

translation_client = get_translation_client()

object_store_client = get_object_store_client()

pdf_client = TranslatePdfClient()
docx_client = TranslateDocxClient()
md_client = TranslateMdClient()

api_client = ApiClient(translation_client=translation_client, object_store_client=object_store_client, pdf_client=pdf_client, docx_client=docx_client, md_client=md_client)

@app.post("/")
async def process_action(request: Request):
    body = await request.json()
    req_params_dict = dict(request.query_params)
    action = req_params_dict["action"] if "action" in req_params_dict else None
    if action == "health-check":
        api_client.health_check()

    if action == "translate":
        text = body["text"]
        source_language = body["source_language"]
        target_language = body["target_language"]
        model_id = body["model_id"]
        region = body["region"]
        return api_client.translate_text(text, source_language, target_language, extra_params={model_id, region})

    elif action == "translate-file":
        get_url = body["get_url"]
        put_url = body["put_url"]
        scale = body["scale"] if "scale" in body else 0.5
        source_language = body["source_language"]
        target_language = body["target_language"]
        model_id = body["model_id"]
        region = body["region"]
        original_file_name = body["original_file_name"]
        return api_client.translate_file(get_url, put_url,  original_file_name, source_language, target_language, scale, extra_params={model_id, region})
 
    elif action == "get-presigned-url":
        client_action = body["client_action"]
        if(not client_action):
            raise HTTPException(status_code=500, detail="Invalid client action")
            
        file_name = body["name"]
        if(not file_name):
            raise HTTPException(status_code=400, detail="file name is not given!")
            
        url =  object_store_client.create_url(file_name, client_action)
        return url

    elif action == "delete-file":
        file_name = body["name"]
        if(not file_name):
            raise HTTPException(status_code=400, detail="file name is not given!")
                
        return object_store_client.delete_file(file_name)
    
    elif action == "custom-prompt":
        prompt = body["prompt"]
        model_id = body["model_id"]
        region = body["region"]
        if(not prompt or not model_id or not region):
            raise HTTPException(status_code=400, detail="provide prompt, model_id and region!")
           
        bedrock = BedRockClient()
        return bedrock.custom_prompt(prompt, model_id, region)

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    

@app.post("/translate-file-static")
async def translate_document():
   return api_client.translate_file("https://nllb-files.s3.eu-north-1.amazonaws.com/Curriculum-+Solar+Systems+Installer.pdf", "https://nllb-files.s3.eu-north-1.amazonaws.com/Curriculum-+Solar+Systems+Installer-egnlish.pdf", "test.pdf","arabic","english", 0)



@app.post("/custom-prompt")
async def custom_prompt(prompt, model_id, region):
    bedrock = BedRockClient()
    return bedrock.custom_prompt(prompt, model_id, region)

nest_asyncio.apply()
uvicorn.run(app, port=8000)