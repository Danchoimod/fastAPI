import os
import uuid
from google.cloud import storage
from src.config import settings

class GCSService:
    def __init__(self):
        self.credentials_path = settings.GCS_CREDENTIALS_FILE
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.client = None
        self.bucket = None
        
        # Initialize client
        if os.path.exists(self.credentials_path):
            try:
                self.client = storage.Client.from_service_account_json(self.credentials_path)
            except Exception as e:
                print(f"Error connecting to GCS: {e}")
        else:
            print(f"GCS credentials file not found at: {self.credentials_path}")

    def _ensure_bucket(self):
        if not self.client:
            raise Exception("GCS Service is not initialized. Credentials file is missing or invalid.")
        if not self.bucket:
            # We directly initialize the bucket object.
            # We bypass the exists() check because the service account might not have storage.buckets.get permission
            # but still has storage.objects.create permission on the bucket.
            self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        """
        Uploads a file to GCS and returns its public URL.
        """
        self._ensure_bucket()
        
        # Generate a unique path for the file to prevent overwrites
        unique_id = uuid.uuid4().hex
        ext = os.path.splitext(filename)[1]
        gcs_filename = f"uploads/{unique_id}{ext}"
        
        blob = self.bucket.blob(gcs_filename)
        
        # Upload from string/bytes
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Make the blob publicly viewable (optional, might fail if uniform bucket-level access is on)
        try:
            blob.make_public()
        except Exception:
            pass
            
        return blob.public_url

    def delete_file(self, file_url: str) -> bool:
        """
        Deletes a file from GCS based on its public URL.
        """
        self._ensure_bucket()
        
        try:
            # Extract GCS object path from public URL
            prefix = f"https://storage.googleapis.com/{self.bucket_name}/"
            if file_url.startswith(prefix):
                blob_name = file_url[len(prefix):]
                blob = self.bucket.blob(blob_name)
                # Attempt delete directly
                blob.delete()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file from GCS: {e}")
            return False

# Singleton instance
gcs_service = GCSService()
