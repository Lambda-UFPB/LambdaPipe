import os
import gzip


def get_file_name(path):
    file_name = path.split("/")
    file_name = file_name[-1]
    return file_name


def unzip(zipped_path):
    # vai ter que pegar o último
    unzipped_path = zipped_path.replace(".gz", "")
    with gzip.open(zipped_path, 'rb') as zipped:
        with open(unzipped_path, 'wb') as unzipped:
            unzipped.write(zipped.read())
    return unzipped_path


def get_last_file():
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_path = os.popen(cmd_1).read()
    download_path = download_path.replace("\n", "")
    all_files = os.listdir(download_path)
    only_pharmit = []
    for file in all_files:
        if 'pharmit' in file:
            only_pharmit.append(file)
    pharmit_files = [os.path.join(download_path, file) for file in only_pharmit]
    while True:
        most_recent = max(pharmit_files, key=os.path.getmtime)
        if 'crdownload' not in most_recent:
            break

    return most_recent
