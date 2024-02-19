import os
import random
import string
import glob
import gzip
import pandas as pd
import re
import time
from exceptions import InvalidInputError


def get_absolute_path(path: str):
    return os.path.abspath(path)


def create_stats_file(output_folder_path: str):
    with open(f'{output_folder_path}/results/search-stats.txt', 'w') as stats:
        stats.write('Search Log\n\n')


def transfer_to_folder(old_path: str, new_path: str, opt: str):
    cmd = f"{opt} '{old_path}' {new_path}"
    os.system(cmd)


def check_session(session: dict):
    if not session["ligand"] or not session["points"]:
        raise InvalidInputError("You must provide a valid receptor and ligand in the correct order")


def generate_folder_name():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(8))


def write_stats(text: str, output_folder_path: str):
    with open(f"{output_folder_path}/results/search-stats.txt", "a") as stats:
        stats.write(text)


def get_file_name(path: str):
    file_name = path.split("/")
    file_name = file_name[-1]
    return file_name


def create_folders(folder_name: str):
    output_folder_path = f"{os.getcwd()}/files/{folder_name}"
    if not os.path.exists(output_folder_path):
        cmd = f"mkdir {output_folder_path}; mkdir {output_folder_path}/admet; mkdir {output_folder_path}/results"
        os.system(cmd)
    else:
        raise FileExistsError(f"{output_folder_path} already exists")

    return output_folder_path


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


def get_download_list(file_pattern: str):
    cmd_1 = "xdg-user-dir DOWNLOAD"
    download_directory_path = os.popen(cmd_1).read()
    download_directory_path = download_directory_path.replace("\n", "")
    download_list = glob.glob(os.path.join(download_directory_path, file_pattern))
    return download_list


def get_last_files(file_pattern: str, old_download_list: list = None, minimize_count: int = None):
    most_recent = ''
    if not old_download_list:
        old_download_list = []
    while True:
        download_list = get_download_list(file_pattern)
        # Filter out files that are still being downloaded or do not exist
        download_list = [f for f in download_list if os.path.isfile(f) and not f.endswith('.crdownload')]
        download_list.sort(key=os.path.getmtime, reverse=True)
        if len(download_list) > len(old_download_list) and file_pattern == 'pharmit*.json*':
            try:
                most_recent = download_list[0]
            except IndexError:
                time.sleep(1)
                continue
            break
        elif minimize_count:
            most_recent = download_list[:minimize_count]
            break

    return most_recent
     

if __name__ == '__main__':
    download_path = get_last_files('pharmit*.json*')
    print(download_path)
