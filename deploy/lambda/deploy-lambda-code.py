import os
import zipfile
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

folders_to_zip = ['./services', './utils','.'] # '.' mean current directory

# lambda config 
LAMBDA_FUNCTION_NAME = os.environ["LAMBDA_FUNCTION_NAME"]
LAMBDA_REGION_NAME = os.environ["LAMBDA_REGION_NAME"]

def zip_folder(folder_path, zipf, is_recursive=True):
    """
    Adds files from the given folder to the zip file.

    Args:
        folder_path (str): Path to the folder to be zipped.
        zipf (zipfile.ZipFile): Open zip file object.
        is_recursive (bool): If True, adds files from subdirectories recursively.
    """
    if is_recursive:
        # Recursively add all .py files from folder and subfolders
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py') and 'MinIOClient' not in file:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.getcwd())
                    zipf.write(file_path, arcname)
    else:
        # Add only .py files from the given folder (non-recursive)
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if file.endswith('.py') and os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))

def zip_current_folder(zip_name):
    """
    Zips specific folders and files into a zip archive.

    Args:
        zip_name (str): Name of the output zip file.
    """
    current_dir = os.getcwd()

    # Create a zip file with compression
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Step 1: Add .py files from the root directory (non-recursive)
        zip_folder(current_dir, zipf, is_recursive=False)

        # Step 2: Add subdirectories recursively (e.g., 'lambda-layer/')
        dirs_to_copy = ['./services','./utils']
        for directory in dirs_to_copy:
            subfolder = os.path.join(current_dir, directory)
            if os.path.exists(subfolder):
                zip_folder(subfolder, zipf, is_recursive=True)

        # Step 3: Add 't.py' from '/deploy/lambda/' to the root of the zip
        lambda_entrypoint = 'lambda_function.py'
        lambda_file = os.path.join(current_dir, 'deploy', 'lambda', lambda_entrypoint)
        if os.path.isfile(lambda_file):
            zipf.write(lambda_file, lambda_entrypoint)

    print(f"Files zipped successfully into '{zip_name}'.")

def upload_zip_to_lambda(zip_name, function_name):
    client = boto3.client('lambda', region_name=LAMBDA_REGION_NAME)

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
    zip_name = 'lambda_function_code.zip'
    
    # Call the function to zip the folder
    zip_current_folder(zip_name)
        
    # Upload the zip file to AWS Lambda
    upload_zip_to_lambda(zip_name, LAMBDA_FUNCTION_NAME)

    # remove zip file
    os.remove(zip_name)

# To run locally
if __name__ == "__main__":
    upload()
