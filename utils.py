import os
import random
import string
import glob
import gzip
import pandas as pd
import re
import time


def transfer_to_folder(old_path: str, new_path: str, opt: str):
    cmd = f"{opt} '{old_path}' {new_path}"
    os.system(cmd)


def generate_folder_name():
    letters_and_digits = string.ascii_letters + string.digits

    return ''.join(random.choice(letters_and_digits) for _ in range(8))


def create_folders(folder_name: str):
    output_folder_path = f"{os.getcwd()}/files/{folder_name}"
    if not os.path.exists(output_folder_path):
        cmd = f"mkdir {output_folder_path}; mkdir {output_folder_path}/admet; mkdir {output_folder_path}/results"
        os.system(cmd)
    else:
        raise FileExistsError(f"{output_folder_path} already exists")

    return output_folder_path


def get_file_name(path: str):
    file_name = path.split("/")
    file_name = file_name[-1]
    return file_name


def merge_csv(csv_files_path: str):
    csv_files = glob.glob(f"{csv_files_path}/admetcsv_*.csv")
    csv_files.sort(key=lambda x: int(re.findall(r'admetcsv_(\d+)\.csv', x)[0]))
    merged_csv = pd.concat([pd.read_csv(file) for file in csv_files])
    merged_csv.to_csv(f"{csv_files_path}/merged.csv", index=False)
    for f in csv_files:
        os.remove(f)


def get_chrome_binary_path():
    cmd_a = "which google-chrome"
    cmd_b = "which google-chrome-stable"
    possible_path_1 = os.popen(cmd_a).read()
    possible_path_2 = os.popen(cmd_b).read()
    return [possible_path_1.replace("\n", ""), possible_path_2.replace("\n", "")]


def unzip(zipped_path):
    unzipped_path = zipped_path.replace(".gz", "")
    with gzip.open(zipped_path, 'rb') as zipped:
        with open(unzipped_path, 'wb') as unzipped:
            unzipped.write(zipped.read())
    os.remove(zipped_path)
    return unzipped_path


def get_absolute_path(path: str):
    return os.path.abspath(path)


def get_last_files(file_pattern: str, minimize_count: int = None):
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_path = os.popen(cmd_1).read()
    download_path = download_path.replace("\n", "")
    print(download_path)
    download_list = glob.glob(os.path.join(download_path, file_pattern))
    most_recent = ''

    download_list.sort(key=os.path.getmtime, reverse=True)
    
    if file_pattern == 'pharmit*.json':
        while True:
            try:
                most_recent = download_list[0]
            except IndexError:
                time.sleep(2)
                continue
            if 'crdownload' not in most_recent:
                break
    if minimize_count:
        most_recent = download_list[:minimize_count]
    
    return most_recent
     

if __name__ == '__main__':
    #a = get_last_files('minimized_results*', 10)
    nometeste = generate_folder_name()
    out_path = create_folders(nometeste)
    print(out_path)
