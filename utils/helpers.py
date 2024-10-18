
import json
from urllib.parse import unquote

def response_object(status_code:int, body, headers={
                    "Access-Control-Allow-Origin": "*", 
                    'Content-Type': "application/json", 
                     'Access-Control-Allow-Methods': '*',

                }):
    return {
            'statusCode': status_code,
            'body': json.dumps(body),
            'headers': headers,
    }

def decode_url(url):
    return unquote(url)