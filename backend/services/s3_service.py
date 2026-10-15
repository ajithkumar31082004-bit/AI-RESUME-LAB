"""
AI RESUME LAB — S3 & Storage Service
Handles uploading resume files to AWS S3, generating presigned URLs,
and falls back gracefully to local disk storage if AWS credentials are not configured.
"""
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, app=None):
        self.app = app
        self._s3_client = None

    def _get_s3_client(self):
        """Lazy load boto3 S3 client if configured."""
        if self._s3_client is not None:
            return self._s3_client

        aws_key = current_app.config.get("AWS_ACCESS_KEY_ID")
        aws_secret = current_app.config.get("AWS_SECRET_ACCESS_KEY")
        aws_region = current_app.config.get("AWS_REGION", "us-east-1")
        bucket = current_app.config.get("S3_BUCKET_NAME")

        if aws_key and aws_secret and bucket:
            try:
                import boto3
                self._s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    region_name=aws_region,
                )
                logger.info(f"Initialized S3 client for bucket: {bucket}")
                return self._s3_client
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {e}. Falling back to local storage.")
                return None
        return None

    def save_file(self, file_storage, user_id=None) -> dict:
        """
        Saves uploaded file to S3 or local upload folder.
        Returns metadata dictionary:
        {
            "filename": str,
            "original_filename": str,
            "file_path": str,
            "file_size": int,
            "file_type": str,
            "s3_key": str or None,
            "s3_url": str or None
        }
        """
        orig_filename = secure_filename(file_storage.filename or "resume.pdf")
        ext = orig_filename.rsplit(".", 1)[-1].lower() if "." in orig_filename else "pdf"
        unique_name = f"{uuid.uuid4().hex}_{orig_filename}"

        # Calculate file size
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
        file_storage.seek(0)

        s3_client = self._get_s3_client()
        bucket = current_app.config.get("S3_BUCKET_NAME")
        s3_key = None
        s3_url = None
        local_path = None

        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        local_path = os.path.join(upload_folder, unique_name)

        # Always save a local copy for text extraction / backup
        file_storage.save(local_path)
        file_storage.seek(0)

        # Upload to S3 if available
        if s3_client and bucket:
            try:
                s3_key = f"resumes/{user_id or 'anonymous'}/{unique_name}"
                extra_args = {"ContentType": file_storage.content_type or "application/octet-stream"}
                s3_client.upload_fileobj(file_storage, bucket, s3_key, ExtraArgs=extra_args)

                # Generate public URL or presigned URL
                s3_url = f"https://{bucket}.s3.{current_app.config.get('AWS_REGION', 'us-east-1')}.amazonaws.com/{s3_key}"
                logger.info(f"Successfully uploaded {orig_filename} to s3://{bucket}/{s3_key}")
            except Exception as e:
                logger.error(f"S3 upload error: {e}. Keeping local copy only.")
                s3_key = None
                s3_url = None

        return {
            "filename": unique_name,
            "original_filename": orig_filename,
            "file_path": local_path,
            "file_size": file_size,
            "file_type": ext,
            "s3_key": s3_key,
            "s3_url": s3_url,
        }

    def get_download_url(self, s3_key: str, expires_in=3600) -> str:
        """Generate presigned S3 URL for temporary download."""
        s3_client = self._get_s3_client()
        bucket = current_app.config.get("S3_BUCKET_NAME")
        if s3_client and bucket and s3_key:
            try:
                return s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": s3_key},
                    ExpiresIn=expires_in,
                )
            except Exception as e:
                logger.error(f"Failed to generate presigned S3 URL: {e}")
        return None

    def delete_file(self, s3_key: str = None, local_path: str = None) -> bool:
        """Deletes file from S3 and local storage."""
        success = True
        if s3_key:
            s3_client = self._get_s3_client()
            bucket = current_app.config.get("S3_BUCKET_NAME")
            if s3_client and bucket:
                try:
                    s3_client.delete_object(Bucket=bucket, Key=s3_key)
                except Exception as e:
                    logger.error(f"Failed to delete S3 object {s3_key}: {e}")
                    success = False
        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception as e:
                logger.error(f"Failed to remove local file {local_path}: {e}")
                success = False
        return success


storage_service = StorageService()
