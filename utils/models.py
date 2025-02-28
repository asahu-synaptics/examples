import os
import requests
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def download(repo_id, file_path):
    local_dir = './models'
    os.makedirs(local_dir, exist_ok=True)
    local_file = os.path.join(local_dir, os.path.basename(file_path))
    
    logger.debug(f"Checking if file exists locally at: {local_file}")
    if os.path.exists(local_file):
        logger.debug(f"File found. Model already exists locally at: {local_file}")
        return local_file

    local_server = os.environ.get('SYNAPTICS_SERVER_IP', '192.168.50.10')
    url = f'http://{local_server}/downloads/models/{repo_id}/{file_path}'
    logger.debug(f"Constructed URL: {url}")
    
    try:
        logger.debug("Sending GET request to local server.")
        r = requests.get(url, timeout=5)
        logger.debug(f"Received response with status code: {r.status_code}")
        if r.status_code == 200:
            logger.debug("Status 200 OK. Writing content to local file.")
            with open(local_file, 'wb') as f:
                f.write(r.content)
            logger.debug("File written successfully.")
            return local_file
        else:
            logger.debug(f"Local server error (status: {r.status_code}). Falling back to Hugging Face.")
    except Exception as e:
        logger.debug(f"Error fetching from local server: {e}. Falling back to Hugging Face.")

    # Uncomment the following lines to fall back to Hugging Face Hub download.
    # logger.debug("Attempting to download model from Hugging Face Hub.")
    # local_file = hf_hub_download(
    #     repo_id=repo_id,
    #     filename=file_path,
    #     local_dir=local_dir
    # )
    # logger.debug("Download from Hugging Face completed.")
    # return local_file
