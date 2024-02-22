import os
import re
import shutil


def remove_directory(path):
    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def get_clean_file_name(file_name, delimiter):
    clean_file_name = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", delimiter, file_name)
    return clean_file_name
