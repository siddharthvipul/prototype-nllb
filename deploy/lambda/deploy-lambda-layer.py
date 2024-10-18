import os
import zipfile
import boto3
from botocore.exceptions import NoCredentialsError
from os import listdir
from os.path import isfile, join

def zip_current_folder(zip_name):
    # Get the current working directory
    folder_to_zip = os.path.join(os.getcwd(),'lambda-layer')
    
    # Create a zip file
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    
    onlyfiles = [f for f in listdir(folder_to_zip) if isfile(join(folder_to_zip, f)) and f.endswith(".py")]

    for file in onlyfiles:
        file_path = os.path.join(os.getcwd(), file)
        arcname = os.path.relpath(file_path, folder_to_zip)
        zipf.write(file_path, arcname)
    
    zipf.close()
    print(f"Folder '{folder_to_zip}' zipped successfully into '{zip_name}'.")

def upload_zip_to_lambda(zip_name, function_name):
    client = boto3.client('lambda')

    try:
        with open(zip_name, 'rb') as zip_file:
            zip_content = zip_file.read()

        response = client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )

        print(f"Successfully uploaded the zip to Lambda function '{function_name}'.")
        return response

    except NoCredentialsError:
        print("AWS credentials not available.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def upload():
    # Specify the zip file name
    zip_name = 'lambda_function_layer.zip'
    
    # Call the function to zip the folder
    zip_current_folder(zip_name)
    
    function_name = 'nllb-backend'
    
    # Upload the zip file to AWS Lambda
    upload_zip_to_lambda(zip_name, function_name)

    # remove zip file
    os.remove(zip_name)


# To run locally
if __name__ == "__main__":
    upload()
