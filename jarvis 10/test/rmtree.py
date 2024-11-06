import os, shutil

def remove_dir_inside_files(dir):
    # it removes all files inside dir
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


if __name__ == "__main__":
    remove_dir_inside_files("data\sql")