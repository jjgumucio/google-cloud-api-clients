from oauth2client.client import GoogleCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from apiclient.errors import HttpError


class CloudStorageClient:
    def __init__(self):
        self.credentials = GoogleCredentials.get_application_default()
        self.service = build('storage', 'v1', credentials=self.credentials)

    def upload_media(self, bucket, objectName, mediaBody):
        MediaFileUpload(mediaBody, chunksize=-1)
        result = self.service.objects().insert(bucket=bucket,
                                               name=objectName,
                                               media_body=mediaBody).execute()
        return result

    def list_files(self, bucket):
        result = self.service.objects().list(bucket=bucket).execute()
        return result

    def download_media(self, bucket, objectName):
        try:
            result = self.service.objects().get_media(
                bucket=bucket, object=objectName).execute()
            return result
        except:
            return None

    def delete_media(self, bucket, objectName):
        try:
            self.service.objects().delete(bucket=bucket,
                                          object=objectName).execute()
            return True
        except HttpError as e:
            return e


def run(action, bucket, obj_name):

    gcs_service = CloudStorageClient()

    if action == "1":
        print "# - Uploading file: %s to %s - #" % (obj_name, bucket)
        gcs_service.upload_media(bucket, obj_name, obj_name)
        print "# - Successfully uploaded file - #"

    elif action == "2":
        print "# - Downloading file %s - #" % obj_name
        gcs_service.download_media(bucket, obj_name)
        print "# - Succesfully downloaded file - #"


def main():
    action = raw_input("Enter action to perform ('1'= upload, '2'=download): ")
    bucket = raw_input("Enter the bucket name to upload to: ")
    obj_name = raw_input("Enter the file name to be uloaded: ")

    run(action, bucket, obj_name)

if __name__ == "__main__":
    main()
