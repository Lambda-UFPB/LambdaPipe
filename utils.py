import os
import gzip


def get_path(filename):
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_path = os.popen(cmd_1).read()
    download_path = download_path.replace("\n", "")
    download_path = download_path + f"/{filename}"
    new_path = f"{os.getcwd()}/files"
    return download_path, new_path


def remove_previous(filename):
    download_path, _ = get_path(filename)
    if os.path.exists(download_path):
        os.remove(download_path)


def unzip(zipped_path):
    unzipped_path = zipped_path.replace(".gz", "")
    remove_previous(unzipped_path)
    with gzip.open(zipped_path, 'rb') as zipped:
        with open(unzipped_path, 'wb') as unzipped:
            unzipped.write(zipped.read())
    return unzipped_path
