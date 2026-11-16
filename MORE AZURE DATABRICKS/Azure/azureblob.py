import os
from azure.storage.blob import BlobServiceClient, StandardBlobTier

conn_str = os.environ["AZURE_STORAGE_CONN_STR"]

blob_service = BlobServiceClient.from_connection_string(conn_str)
blob_client = blob_service.get_blob_client(container='raw', blob='raw/2024/01/data.parquet')
 
# Upload with a specific access tier
with open('data.parquet', 'rb') as f:
    blob_client.upload_blob(f, standard_blob_tier=StandardBlobTier.COOL)
 
# Change tier of an existing blob
blob_client.set_standard_blob_tier(StandardBlobTier.ARCHIVE)