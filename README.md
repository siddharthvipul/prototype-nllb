# NLLB

This is the repository for a NLLB prototype. The prototype allows to use different LLM models for text and file translation. The code is model-agnostic. You can plugin your own models as long as they support the main interface. We want to use open-source models ofcouse for our implementation.

## Structure
The prototype defines and API interface in the services/api.py file. These apis are used to translate text and files. Each api call requires user to provide model information so it is completely model-agnostic.

Anyone can use this api for their usecases. Right now, we have implemented two ways of deploying either using a lambda or a fast api server but they can be extended to more.

Right now the models we support for translation are:
- Bedrock Models (using llama 3 and llama 3.1 but can be extended to more by simply providing model id)
- Google translator (used for testing purposes mostly)
- Custom models deployed on bedrock

Note: For bedrock models, you need to request access to the models to use them.

For file translation, we support:
- PDF files
- DOCX files
- MD files
- PPT files (not direct support, ppt must be downloaded as pdf and then translated, then can be converted back to ppt using `convert_pdf_to_ppt.py` file)

## Deploy

Populate the bucket name and region for S3 in .env file.

### Lambda

To deploy prototype on lambda, follow the below steps:

#### Create Dependencies Layer

- First create lambda layer for dependencies if does not already exist.

```console
cd lambda-layer
```

- Make sure all dependencies needed are added to requirements.txt.
- Run install script to create layers zip file.

```console
sh ./install.sh
```

- Upload the lambda_layers.zip folder on AWS Lambda layers.

#### Uploading code to Lambda
- Create a zip folder of root directory. You do not need to include the lambda-layer directory. Its fine either way.
- Upload the zip on the lambda located.
- Attach the lambda layer with the function if not done. The option is under Layers. You can see which version of layer is attached and edit to change if necessary.
- Run deploy and done!
- Configure to use API Gateway with the lambda and use that to invoke the lambda.
- Lambda was deployed with python-3.8 to work. Might work with later versions you can try it out.
- You can also use this script to deploy code:

```console
python deploy/lambda/deploy-lambda-code.py
```

To use the script, first create a .env follwing the .env.example file and then enter the lambda function name and region. You should have your AWS credentials set up for this and have permission to access the specified lambda function.

#### Making changes
- To make changes to lambda function simply make the change and follow above steps again.
- You only need to redeploy and reattach the layer if any dependency was changed/added/removed.
- You can update the code on the lambda directly but choose to do it this way so we can track changes and easily track back if needed.

### Fast Server

It is recommended to use venv for isolation but up to you. To deploy prototype on server, follow the below steps:

#### Install dependencies

```console
pip install -r deploy/server/requirements.txt
```

#### Run Server

```console
python deploy/server/server.py
```

### Configuration

You can use your own object store implementation by extending the object_store class in `services/object_store/ObjectStoreClient.py`. This implementation has been tested with MinIO and works without need for modication.

Then just add the implementation to `utils/client.py` file in the `get_object_store_client` function. Now specify that type in api_client initialization for the mode of deployment (server, lambda) you want to use.

Similary, you can modify the translation you want to use by adding that in the translators package and following the api that `bedrock.py` follows. For example, we have a mock implementation in this project in `services/translators/mock.py`.
Then just add that implementation in `utils/client.py` in get_translation_client function. Like for object store, specify that type in api_client initialization for the mode of deployment (server, lambda) you want to use.

### Sample Request

#### Text Translation

```console
curl  -X POST \
  'localhost:8000/?action=translate' \
  --header 'Accept: */*' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "model_id": "meta.llama3-1-8b-instruct-v1:0",
  "region": "us-west-2",
  "source_language":"english",
  "target_language": "french",
  "text": "Hello, there! General Kenobi"

}'

```

#### File Translation

- First get presigned-urls for a file-name:

- For Put action (to upload file)

```console
curl  -X POST \
  'http://127.0.0.1:8000/?action=get-presigned-url' \
  --header 'Accept: */*' \
  --header 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
  --header 'Content-Type: application/json' \
  --data-raw '{
  "client_action":"put_object",
  "name":"filename" // file name with extension
}'
```

- Use the put url to upload the file. You can use this as an [example]()
- Then send request to translate file:

```console
curl  -X POST \
  'http://127.0.0.1:8000/?action=translate-file' \
  --header 'Accept: */*' \
  --header 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
  --header 'x-api-key: gNP5Kdejmf2LyQJJHFodJ7pnzIVdahcs7gLjoNev' \
  --header 'Content-Type: application/json' \
  --data-raw '{
  "get_url":"", //add value
  "put_url":"", // add value
  "model_id": "meta.llama3-1-8b-instruct-v1:0",
  "region": "us-west-2",
  "source_language":"english",
  "target_language": "french",
  "original_file_name": "fileName" // file name with extension
}'
```

- You can then get the file using the Get url
- For Get action (to donwload file)

```console
curl  -X POST \
  'http://127.0.0.1:8000/?action=get-presigned-url' \
  --header 'Accept: */*' \
  --header 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
  --header 'Content-Type: application/json' \
  --data-raw '{
  "client_action":"get_object",
  "name":"filename"
}'
```


### Links for Learning
- https://ai.meta.com/research/no-language-left-behind/
- https://aws.amazon.com/bedrock/

# Legal 🧑‍⚖️📜

The prototype allows to use different LLM models for text and file translation.
Copyright (C) 2024 UNICEF

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
