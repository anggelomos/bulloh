import boto3


class AWSController:

    def __init__(self):
        self.bulloh_bucket_name = "bulloh-data"
        self.s3_client = boto3.client('s3')

    def download_file(self, file_path, file_name):
        self.s3_client.download_file(self.bulloh_bucket_name, file_name, file_path)

    def upload_file(self, file_path, file_name):
        self.s3_client.upload_file(file_path, self.bulloh_bucket_name, file_name)
