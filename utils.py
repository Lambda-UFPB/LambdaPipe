import os
import glob
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


def get_last_files(file_pattern: str, minimize_count: int = None):
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_path = os.popen(cmd_1).read()
    download_path = download_path.replace("\n", "")
    download_list = glob.glob(os.path.join(download_path, file_pattern))

    download_list.sort(key=os.path.getmtime, reverse=True)
    
    if file_pattern == 'pharmit*.json':
        while True:
            most_recent = download_list[0]
            if 'crdownload' not in most_recent:
                break
    if minimize_count:
        most_recent = download_list[:minimize_count]
    
    return most_recent
     

if __name__ == '__main__':
    a = get_last_files('minimized_results*', 10)
    #print(get_chrome_binary_path())
