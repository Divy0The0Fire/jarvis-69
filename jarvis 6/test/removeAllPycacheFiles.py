import os
import shutil

def remove_pycache_dirs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            shutil.rmtree(pycache_path)
            print(f'Removed: {pycache_path}')

# Replace 'your_directory' with the path to the directory you want to clean
remove_pycache_dirs(f'{os.getcwd()}')
