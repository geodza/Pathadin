import os
import shutil


def make_if_not_exists(filepath: str, delete=False) -> None:
    d = os.path.dirname(filepath)
    if os.path.exists(d) and delete:
        shutil.rmtree(d)
    if d and not os.path.exists(d):
        os.makedirs(d)


def write(filepath: str, value: str) -> None:
    make_if_not_exists(filepath)
    with open(filepath, mode='w') as f:
        f.write(value)


def remove_if_exists(filepath: str) -> None:
    if os.path.exists(filepath):
        os.remove(filepath)


# Delete everything reachable from the directory named in "top",
# assuming there are no symbolic links.
# CAUTION:  This is dangerous!  For example, if top == '/', it
# could delete all your disk files.
def delete_folder_recursively(folder: str) -> None:
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
