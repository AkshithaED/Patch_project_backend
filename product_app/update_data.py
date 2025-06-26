import requests
import logging
import sys
import time
import os

PRIVATE_TOKEN = os.getenv("PRIVATE_TOKEN", "8b7bQ6mYoHNNKPJX6Yz4")

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.otxlab.net/api/v4")
PROJECT_ID = os.getenv("PROJECT_ID", "115935")
BOT_JOB_NAME = os.getenv("BOT_JOB_NAME", "dummy")

def trigger_pipeline(CMD: str, patch_input: str = None, product_input: str = None) -> int:
    """
    Trigger a single GitLab pipeline passing patch_input and product_input as variables.
    """
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/pipeline"
    headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}
    variables = {"CMD": CMD}
    
    # Only add variables if they are set
    if patch_input:
        variables["PATCH_INPUT"] = patch_input
    if product_input:
        variables["PRODUCT_INPUT"] = product_input

    data = [("ref", "main")]
    for key, value in variables.items():
        data.append((f"variables[][key]", key))
        data.append((f"variables[][value]", value))

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    pipeline_id = response.json()["id"]
    logging.info(f"Triggered pipeline ID: {pipeline_id} with variables: {variables}")
    return pipeline_id

def wait_for_pipeline(pipeline_id: int, timeout: int = 1800) -> str:
    url = f"{GITLAB_URL}/projects/{PROJECT_ID}/pipelines/{pipeline_id}"
    headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

    start = time.time()
    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        status = response.json()["status"]
        logging.info(f"Pipeline {pipeline_id} status: {status}")
        if status in ("success", "failed", "canceled"):
            return status
        if time.time() - start > timeout:
            raise TimeoutError(f"Pipeline {pipeline_id} status check timed out")
        time.sleep(10)

def update_details(patch_input=None, product_input=None):
    # We trigger one pipeline per patch or patch+product combo
    try:
        pipeline_id = trigger_pipeline("update", patch_input, product_input)
        status = wait_for_pipeline(pipeline_id)
        if status != "success":
            logging.error(f"Pipeline {pipeline_id} failed with status: {status}")
            sys.exit(1)
        logging.info(f"Pipeline {pipeline_id} completed successfully.")
    except Exception as e:
        logging.error(f"Error during pipeline run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Patch Image Orchestrator")
    parser.add_argument("--patch", help="Patch name or ID")
    parser.add_argument("--product", help="Product name")
    args = parser.parse_args()
    update_details(args.patch, args.product)
