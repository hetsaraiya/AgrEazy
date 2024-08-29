from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client
from io import BytesIO

class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET
        self.supabase = create_client(self.supabase_url, self.supabase_key)

    def _save(self, name, content):
        # Convert content to bytes for uploading
        file_content = BytesIO(content.read())
        
        # Upload the file to the specified bucket in Supabase
        response = self.supabase.storage.from_(self.bucket_name).upload(name, file_content.read())
        
        if response.get('error'):
            raise Exception(f"Error uploading to Supabase: {response['error']['message']}")
        
        # Return the path where the file was uploaded
        return response['data']['path']

    def url(self, name):
        # Get the public URL of the file in Supabase
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

    def exists(self, name):
        # Check if a file exists in Supabase
        response = self.supabase.storage.from_(self.bucket_name).list()
        return any(file['name'] == name for file in response['data'])

    def delete(self, name):
        # Delete the file from Supabase
        self.supabase.storage.from_(self.bucket_name).remove([name])
