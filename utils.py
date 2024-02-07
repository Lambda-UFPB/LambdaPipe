import os
import gzip


def transfer_to_folder(old_path: str, new_path: str, opt: str):
    cmd = f"{opt} '{old_path}' {new_path}"
    os.system(cmd)


def get_file_name(path: str):
    file_name = path.split("/")
    file_name = file_name[-1]
    return file_name


def unzip(zipped_path):
    unzipped_path = zipped_path.replace(".gz", "")
    with gzip.open(zipped_path, 'rb') as zipped:
        with open(unzipped_path, 'wb') as unzipped:
            unzipped.write(zipped.read())
    os.remove(zipped_path)
    return unzipped_path


def get_chrome_binary_path():
    cmd_a = "which google-chrome"
    cmd_b = "which google-chrome-stable"
    possible_path_1 = os.popen(cmd_a).read()
    possible_path_2 = os.popen(cmd_b).read()
    return [possible_path_1.replace("\n", ""), possible_path_2.replace("\n", "")]


def get_last_files(name: str):
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_path = os.popen(cmd_1).read()
    download_path = download_path.replace("\n", "")
    all_files = os.listdir(download_path)
    only_name = []
    for file in all_files:
        if name in file:
            only_name.append(file)
    name_files = [os.path.join(download_path, file) for file in only_name]

    if name == 'pharmit':
        while True:
            most_recent = max(name_files, key=os.path.getmtime)
            if 'crdownload' not in most_recent:
                break

    else:
        most_recent = sorted(name_files, key=os.path.getmtime, reverse=True)

    return most_recent

if __name__ == '__main__':
    #a = get_last_files('pharmit')
    #print(a)
    print(get_chrome_binary_path())
