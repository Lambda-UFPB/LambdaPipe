import os
import random
import string
import glob
import gzip
import time
from exceptions import InvalidInputError


def get_absolute_path(path: str):
    return os.path.abspath(path)


def create_stats_file(output_folder_path: str):
    with open(f'{output_folder_path}/results/search-stats.txt', 'w') as stats:
        stats.write('Search Log\n\n')


def transfer_to_folder(old_path: str, new_path: str, opt: str):
    cmd = f"{opt} '{old_path}' '{new_path}'"
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


def get_minimized_results_files_list(directory_path):
    path_pattern = os.path.join(directory_path, '*minimized_results*')
    files = glob.glob(path_pattern)
    absolute_paths = [os.path.abspath(file) for file in files]
    return absolute_paths


def unzip_minimized_results_files(files_list: list):
    unzipped_files = []
    for file in files_list:
        if file.endswith('.gz'):
            unzipped_path = unzip(file)
            unzipped_files.append(unzipped_path)
        else:
            unzipped_files.append(file)
    return unzipped_files


def create_folders(folder_name: str, only_process=False):
    folder_name = folder_name.strip()
    output_folder_path = get_absolute_path(folder_name)
    results_folder_path = os.path.join(output_folder_path, "results")
    if only_process:
        folders_to_create = [results_folder_path]
    else:
        folders_to_create = [output_folder_path, results_folder_path]
    for path in folders_to_create:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        else:
            if only_process:
                pass
            else:
                raise FileExistsError()

    return output_folder_path


def process_smiles_file(smiles_file_path: str):
    analyzed_mol_dict = {}
    with open(smiles_file_path, 'r') as f:
        smiles_list = f.readlines()
    smiles_list = [smiles.strip() for smiles in smiles_list]
    for smile in smiles_list:
        analyzed_mol_dict[f'Molecule_{smiles_list.index(smile) + 1}'] = {"score": "NA", "rmsd": "NA", "smiles": smile}

    return analyzed_mol_dict


def get_firefox_binary_path():
    cmd = "which firefox"
    possible_path = os.popen(cmd).read()
    return [possible_path.replace("\n", "")]


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
    download_list.reverse()
    return download_list


def get_last_files(file_pattern: str, old_download_list: list = None, minimize_count: int = None, check_download=False):
    most_recent = ''
    if not old_download_list:
        old_download_list = []
    while True:
        download_list = get_download_list(file_pattern)
        # Filter out files that are still being downloaded or do not exist
        if not check_download:
            download_list = [f for f in download_list if os.path.isfile(f) and not f.endswith('.crdownload')]
        else:
            download_list = [f for f in download_list if os.path.isfile(f) and f not in old_download_list]
        try:
            download_list.sort(key=os.path.getmtime, reverse=True)
        except FileNotFoundError:
            time.sleep(1)
            continue
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


def check_downloads_complete(download_list: list):
    return all('crdownload' not in file for file in download_list)

