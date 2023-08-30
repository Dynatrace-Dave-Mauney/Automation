import os
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
