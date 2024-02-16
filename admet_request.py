import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def get_smiles_string(best_molecules_dict: dict):
    smiles_list = [mol_data['smiles'] for mol_data in best_molecules_dict.values()]
    if len(smiles_list) > 10:
        num_sublists = (len(smiles_list) + 9) // 10
        smiles_sublists = [smiles_list[i*10:(i+1)*10] for i in range(num_sublists)]
        smiles_strings = ['\r\n'.join(sublist) for sublist in smiles_sublists]
        return smiles_strings, smiles_list
    else:
        smiles_string = '\r\n'.join(smiles_list)
        return smiles_string, smiles_list


def get_csv(smiles: list, index: int):
    """Get url for csv file generated by the admetlab portal for the smiles"""
    path = ''
    url = f"https://admetmesh.scbdd.com/service/screening/cal"
    client = requests.session()
    client.get(url=url, timeout=30)
    csrftoken = client.cookies["csrftoken"]
    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "smiles-list": smiles,
        "method": "2"
    }

    with client.post(url, data=payload, headers=dict(Referer=url), stream=True) as r:
        soup = BeautifulSoup(r.content, "html.parser")

    for a in soup.find_all('a', href=True):
        if '/tmp' in a['href']:
            path = a['href']

    csv = f'admetcsv_{index}.csv'

    return path, csv


def download(path, csv, output_folder_path):
    content = requests.get(f"https://admetmesh.scbdd.com{path}").text
    with open(f'{output_folder_path}/admet/{csv}', 'w') as csv_file:
        csv_file.write(content)


def run_admet_request(best_molecules_dict: dict, output_folder_path: str):
    smiles_strings, dict_smiles_list = get_smiles_string(best_molecules_dict)

    with ThreadPoolExecutor(max_workers=len(smiles_strings)) as executor:
        futures = []
        for index, smiles_divided_group in enumerate(smiles_strings):
            futures.append(executor.submit(get_csv, smiles_divided_group, index))
        for future in futures:
            path, csv = future.result()
            download(path, csv, output_folder_path)

    return dict_smiles_list
