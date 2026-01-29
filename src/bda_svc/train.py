import os
import tempfile
from datetime import datetime, timezone
from typing import List

from bda_svc.model import VLM
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

ACCOUNT_URL = "https://vlmimagerepo.blob.core.windows.net"
CONTAINER = "bda-dataset"
***REMOVED***

def train_model(
    account_url: str,
    container_name: str,
    images_prefix: str = "images/",
    runs_prefix: str = "runs/",
) -> str:
    """
    Minimal inference loop:
      - list images from Blob Storage
      - download image
      - write to temp file
      - run VLM.analyze_image(file_path)
      - upload text output to runs/<run_id>/
    """

    # ---- Azure auth ----
    conn_str = AZURE_STORAGE_CONNECTION_STRING
    bsc = BlobServiceClient.from_connection_string(conn_str)
    container = bsc.get_container_client(container_name)

    # ---- Run folder ----
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_out_prefix = f"{runs_prefix.rstrip('/')}/{run_id}/"

    # ---- Init model ----
    vlm = VLM()

    # ---- List image blobs ----
    image_blob_names: List[str] = []
    for blob in container.list_blobs(name_starts_with=images_prefix):
        if blob.name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            image_blob_names.append(blob.name)

    # ---- Core loop ----
    for blob_name in image_blob_names:
        file_name = os.path.basename(blob_name)
        base_name = os.path.splitext(file_name)[0]

        # Download image bytes
        img_bytes = container.get_blob_client(blob_name).download_blob().readall()

        # Write image to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
            tmp.write(img_bytes)
            tmp.flush()

            # Run VLM (expects file path)
            result_text = vlm.analyze_image(tmp.name)

        # Ensure text output
        if not isinstance(result_text, str):
            result_text = str(result_text)

        # Upload output as text file
        out_blob = f"{run_out_prefix}{base_name}.txt"
        container.get_blob_client(out_blob).upload_blob(
            result_text.encode("utf-8"),
            overwrite=True,
            content_type="text/plain; charset=utf-8",
        )

    return run_id


if __name__ == "__main__":
    run_id = train_model(
        account_url=ACCOUNT_URL ,   # e.g. https://<acct>.blob.core.windows.net
        container_name=CONTAINER,  # e.g. bda-dataset
        images_prefix="images/",
        runs_prefix="runs/",
    )
    print("Finished run:", run_id)