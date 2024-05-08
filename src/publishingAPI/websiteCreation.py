import os
import zipfile
from dotenv import load_dotenv

load_dotenv()



def create_or_update_website(local_path, zip_file):
    
    # Create website path if not exists
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    # Save the uploaded file to a temporary location
    file_path = 'temp.zip'
    zip_file.save(file_path)

    """ os.chmod(local_path, 0o644) 
    os.chmod(file_path, 0o644)  """
        
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Iterate throughout zip file to check if 
        # the zip contains only .css and .html files

        file_list = zip_ref.namelist()

        for file_name in file_list:

            if file_name == "css/" or "js/": continue

            if not file_name.endswith('.css') and not file_name.endswith('.html'):
                print("file: ", file_name)
                return 'The zip file should only contain .css and .html files.', 400
        
        
        # Extract all the contents to a directory once files checked
        zip_ref.extractall(local_path)
    
    # Remove the temporary zip file
    os.remove(file_path)

    return 'Website published successfully', 200

