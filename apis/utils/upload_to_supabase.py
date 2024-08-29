from .supabase import supabase_client

def upload_file_to_supabase(file, bucket_name, file_path):
    try:
        # Upload the file to the specified bucket
        response = supabase_client.storage.from_(bucket_name).upload(file_path, file)
        if response['data']:
            return response['data']['path']  # Return the file path or URL after upload
        else:
            print(response['error'])
            return None
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None
