import os
import requests
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def download(repo_id, filename):
    base_dir = './models'
    # Build the local path using repo_id and the entire filename path.
    local_file = os.path.join(base_dir, repo_id, filename)
    os.makedirs(os.path.dirname(local_file), exist_ok=True)
    
    logger.debug(f"Checking if file exists locally at: {local_file}")
    if os.path.exists(local_file):
        logger.debug(f"File found. Model already exists locally at: {local_file}")
        return local_file

    local_server = os.environ.get('SYNAPTICS_SERVER_IP', '192.168.50.10')
    url = f'http://{local_server}/downloads/models/{repo_id}/{filename}'
    logger.debug(f"Constructed URL: {url}")
    
    try:
        logger.debug("Sending GET request to local Synaptics server.")
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
        logger.debug(f"Error fetching from local server: {e}.")

    logger.debug("Attempting to download model from Hugging Face Hub.")
    # Download directly to the desired location.
    downloaded_file = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=os.path.join(base_dir, repo_id)
    )
    logger.debug("Download from Hugging Face completed.")
    return downloaded_file
