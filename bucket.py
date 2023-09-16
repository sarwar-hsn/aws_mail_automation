import os
import boto3


class Bucket:
    def __init__(self):
        #these are for digitalocean
        self.directory_name = 'mailphotos'
        self.bucket_name = os.environ.get('AWS_BUCKET_NAME',None)
        self.region_name=os.environ.get('AWS_BUCKET_REGION_NAME',None)
        self.aws_access_key_id= os.environ.get('AWS_BUCKET_ACCESS_KEY_ID',None)
        self.aws_secret_access_key= os.environ.get("AWS_BUCKET_SECRET_ACCESS_KEY",None)
        self.endpoint_url=os.environ.get('AWS_BUCKET_ENDPOINT_URL',None),

        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            region_name='ams3',
            endpoint_url="https://ams3.digitaloceanspaces.com",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
    
    def _construct_url(self,location):
        return f"https://{self.bucket_name}.{self.region_name}.digitaloceanspaces.com/{location}"
    

    #upload a file to bucket. it will return the url of the uploaded file
    def upload_image(self,local_file_name,uploaded_file_name):
        local_path = f"upload/{local_file_name}"
        upload_location = f"{self.directory_name}/{uploaded_file_name}"
        try:
            self.client.upload_file(
                local_path,#filename in local directory
                self.bucket_name,
                upload_location,
                ExtraArgs={'ACL': 'public-read'}
            )
            return f"{self._construct_url(upload_location)}"
        except:
            return None


    #it will return a list of urls of the files present in bucket
    def get_image_urls(self):
        objects = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.directory_name)
        objects = objects['Contents'][1:]
        images = []
        if objects:
            for obj in objects:
                images.append(self._construct_url(obj.get('Key')))
            return images
        else:
            return None
        
    #deleting a file
    def delete_image(self,filename):
        delete_location = f"{self.directory_name}/{filename}"
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=delete_location
            )
            return True
        except:
            return False


    
   