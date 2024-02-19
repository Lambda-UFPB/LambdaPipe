import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def get_smiles_string(best_molecules_dict: dict):
    smiles_list = [mol_data['smiles'] for mol_data in best_molecules_dict.values()]
    if len(smiles_list) > 5:
        num_sublists = (len(smiles_list) + 4) // 5
        smiles_sublists = [smiles_list[i*5:(i+1)*5] for i in range(num_sublists)]
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
    client.get(url=url, timeout=120)
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


if __name__ == '__main__':
    otp_path = "/home/kdunorat/PycharmProjects/LambdaPipe/files/testedefinitivo"
    dict_final = {'PubChem-163611156': {'score': -16.73157, 'rmsd': 2.32096, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C3C(=C(O[H])C(O[H])=C1O[H])OC1=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(O[H])C(O[H])=C13)=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C3=C(O[H])C(O[H])=C(O[H])C(O[H])=C3C(N([H])[H])(N([H])[H])C2=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-161081531': {'score': -16.59221, 'rmsd': 2.9828, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(O[H])=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C(O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C12'}, 'PubChem-161004308 PubChem-161004311': {'score': -16.45759, 'rmsd': 4.31818, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(O[H])=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C(C5=C(O[H])C6=C(C(O[H])=C(O[H])C(O[H])=C6O[H])C(O[H])=C5O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C12'}, 'PubChem-159527763': {'score': -16.35336, 'rmsd': 3.80713, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C(O[H])=C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C5C(=C(O[H])C(O[H])=C4O[H])OC4=C(O[H])C(O[H])=C(O[H])C(O[H])=C45)C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)C3=C2C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C1O[H]'}, 'PubChem-157883319 PubChem-157883323': {'score': -16.29443, 'rmsd': 4.07498, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(O[H])=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C(C5=C(O[H])C(O[H])=C(O[H])C6=C5C(O[H])=C(O[H])C(O[H])=C6O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C12'}, 'PubChem-166025117': {'score': -15.7038, 'rmsd': 2.6777, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C5C(=C(O[H])C(O[H])=C4O[H])OC4=C(O[H])C(O[H])=C(O[H])C(O[H])=C45)C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C2O[H])C(O[H])=C1O[H]'}, 'PubChem-164124038': {'score': -15.66293, 'rmsd': 3.20353, 'smiles': '[H]OC1=C(O[H])C2=C(C(O[H])=C1O[H])C(C1=C3C(O[H])=C(O[H])C(O[H])=C(O[H])C3=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C3=C1C(O[H])=C(O[H])C(C1=CC=CC4=CC=CC=C41)=C3O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-163456452': {'score': -15.5893, 'rmsd': 2.2007, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1C)C(O[H])=C(O[H])C(C)=C2C1=C(C)C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])=C(O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(O[H])=C(O[H])C2=C1C(O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-163842133': {'score': -15.4792, 'rmsd': 2.92867, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C3C(=C(O[H])C(O[H])=C1O[H])OC1=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(O[H])C(O[H])=C13)=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(C)(C)C2=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-161067846 PubChem-161067849 PubChem-161345061': {'score': -15.34081, 'rmsd': 3.25063, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C3=C1C(O[H])=C(O[H])C(O[H])=C3O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C12'}, 'PubChem-164085166': {'score': -15.2912, 'rmsd': 2.90629, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C12'}, 'PubChem-163545609': {'score': -15.13046, 'rmsd': 2.41004, 'smiles': '[H]OC1=C(C)C(Cl)=C(O[H])C(C2=C(O[H])C3=C(C(O[H])=C2O[H])C(C2=C(O[H])C(O[H])=C(C4=C(O[H])C(O[H])=C(O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C(O[H])=C2O[H])=C2C(O[H])=C(O[H])C(O[H])=C(O[H])C2=C3C2=C(O[H])C(O[H])=C(O[H])C(O[H])=C2O[H])=C1O[H]'}, 'PubChem-162490866': {'score': -14.95306, 'rmsd': 1.96222, 'smiles': '[H]OC1=C(O[H])C2=C(C(O[H])=C1O[H])C(N(C1=CC3=C(SC4=CC=CC=C43)C(C3=CC4=C(C=C3)C3=CC=CC=C3O4)=C1)C1=C(O[H])C(O[H])=C(O[H])C3=C1C(O[H])=C(O[H])C(O[H])=C3O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-159441411': {'score': -14.86034, 'rmsd': 4.24425, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C3OC4=C(O[H])C5=C(C(O[H])=C(O[H])C(O[H])=C5O[H])C(O[H])=C4C3=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(O[H])=C(O[H])C(C2=C(O[H])C(O[H])=C(O[H])C3=C(O[H])C(O[H])=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C32)=C1O[H]'}, 'PubChem-91258151': {'score': -14.71336, 'rmsd': 3.23867, 'smiles': '[H]N([H])C1N([H])C2N([H])C3N([H])C4N([H])C5N([H])C(N([H])[H])N([H])C6N([H])C(N([H])C7N([H])C8N([H])C(N([H])[H])N([H])C9N([H])C(N([H])C%10N([H])C(N1[H])N2C(N3[H])N%10[H])N([H])C(N7[H])N98)N([H])C(N4[H])N56'}, 'PubChem-90912710': {'score': -14.60635, 'rmsd': 4.78802, 'smiles': '[H]N1C2CCCCC2N([H])C2C1C1N([H])C2N([H])C2C3C(C(N2[H])N([H])C2C4C(C(N2[H])N([H])C2C5C(C(N2[H])N1[H])N([H])C1CCCCC1N5[H])N([H])C1CCCCC1N4[H])N([H])C1CCCCC1N3[H]'}, 'PubChem-164036321': {'score': -14.5096, 'rmsd': 3.57958, 'smiles': '[H]OC1=C2C(=C3C(=C1O[H])C(N([H])[H])(N([H])[H])C(N([H])[H])(N([H])[H])C(N([H])[H])(N([H])[H])C3(N([H])[H])N([H])[H])C(N([H])[H])(N([H])[H])C(N([H])[H])(N([H])[H])C(N([H])[H])(N([H])[H])C2(N([H])[H])N([H])[H]'}, 'PubChem-166043360': {'score': -14.42133, 'rmsd': 2.78463, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(O[H])=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C(C5=C(O[H])C(O[H])=C(O[H])C(O[H])C5O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C12'}, 'PubChem-164166650': {'score': -14.41778, 'rmsd': 4.02471, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1)C(O[H])=C(O[H])C1=C2C(C2=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C5OC6=C(C(O[H])=C(O[H])C7=C6C(O[H])=C(O[H])C(O[H])=C7O[H])C5=C4O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C(O[H])C(O[H])=C2O[H])=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-163683385': {'score': -14.39692, 'rmsd': 4.21891, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C(O[H])C(O[H])=C5C(O[H])=C(O[H])C(O[H])=C(O[H])C5=C43)C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C12'}, 'PubChem-157143407': {'score': -14.31826, 'rmsd': 6.1158, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C(O[H])=C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C5OC6=C(O[H])C7=C(C(O[H])=C(O[H])C(O[H])=C7O[H])C(O[H])=C6C5=C4O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)C3=C2C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C1O[H]'}, 'PubChem-123732771': {'score': -14.26079, 'rmsd': 4.48836, 'smiles': '[H]N1CN([H])C2N([H])C(C)N([H])C(C)N([H])C3N([H])C(C)N([H])CN([H])C4N([H])C(C)N([H])C(C)N([H])C5N([H])C(C)N([H])C(C)N([H])C(C)N([H])C6N([H])C(N([H])C(C)N([H])C1C)N([H])C(N2[H])N([H])C(N3[H])N([H])C(N4[H])N([H])C(N5[H])N6[H]'}, 'PubChem-123259177': {'score': -14.15505, 'rmsd': 6.57781, 'smiles': '[H]N1C2C3C=CC(CC3)C2N([H])C2C1C1N([H])C2N([H])C2C3C(C(N2[H])N([H])C2C4C(C(N2[H])N([H])C2C5C(C(N2[H])N1[H])N([H])C1C2C=CC(CC2)C1N5[H])N([H])C1C2C=CC(CC2)C1N4[H])N([H])C1C2C=CC(CC2)C1N3[H]'}, 'PubChem-163567148': {'score': -14.14546, 'rmsd': 3.97156, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(C5=C6C(O[H])=C(O[H])C(O[H])=C(O[H])C6=C(O[H])C6=C5C(O[H])=C(O[H])C(O[H])=C6O[H])=C(O[H])C(O[H])=C4O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C(O[H])C(O[H])=C12'}, 'PubChem-124013728': {'score': -14.13669, 'rmsd': 4.81116, 'smiles': '[H]OC1CC2C(CC1O[H])C1N([H])C2N([H])C2C3CC(O[H])C(O[H])CC3C(N2[H])N([H])C2C3CC(O[H])C(O[H])CC3C(N2[H])N([H])C2C3CC(O[H])C(O[H])CC3C(N2[H])N1[H]'}, 'PubChem-163829364': {'score': -14.09821, 'rmsd': 4.68766, 'smiles': '[H]OC(O[H])=C(C(O[H])=C1OC2=C(O[H])C(O[H])=C3C(O[H])=C(O[H])C(O[H])=C(O[H])C3=C2C1=C)C1=C(O[H])C2=C(C(O[H])=C1O[H])C(C1=C(O[H])C(O[H])=C(O[H])C3=C1C(O[H])=C(O[H])C(O[H])=C3O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(O[H])=C(O[H])C2=C1C(O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-157620259': {'score': -14.04676, 'rmsd': 4.15357, 'smiles': '[H]OC1=C(O[H])C2=C(C(O[H])=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C(F)(F)F)C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C(O[H])=C1O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-91063323': {'score': -14.04058, 'rmsd': 3.90209, 'smiles': '[H]OC1=C(O[H])C2=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(C3=C(O[H])C(O[H])=C(C4=C(O[H])C(O[H])=C(O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C(O[H])=C3O[H])=C2C(O[H])=C1O[H]'}, 'PubChem-163550435': {'score': -14.03891, 'rmsd': 2.14572, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C3C(O[H])=C(O[H])C(O[H])=C(O[H])C3=C(O[H])C(O[H])=C12'}, 'PubChem-91097926': {'score': -14.03872, 'rmsd': 4.41978, 'smiles': '[H]OC1=C(C)C2=C(C(O[H])=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(C)C1=C2C'}, 'PubChem-163518865': {'score': -14.02988, 'rmsd': 3.89807, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C(O[H])=C3C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C5C(=C(O[H])C(O[H])=C4O[H])OC4=C6C(O[H])=C(O[H])C(O[H])=C(O[H])C6=C(O[H])C(O[H])=C45)C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)C(O[H])=C2O[H])C(O[H])=C1O[H]'}, 'PubChem-163605195': {'score': -13.99716, 'rmsd': 5.14168, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C3OC4=C(O[H])C5=C(C(O[H])=C(O[H])C(O[H])=C5O[H])C(O[H])=C4C3=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(C2=C3C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C4C(O[H])(N([H])[H])C3=C(O[H])C(O[H])=C2O[H])=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-164085709': {'score': -13.96128, 'rmsd': 6.94934, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(C3=CC(C4=C5C=CC=CC5=C(C5=C6C(=C(O[H])C(O[H])=C5O[H])OC5=C(O[H])C(O[H])=C(C7=C(O[H])C(O[H])=C(O[H])C(O[H])=C7O[H])C(O[H])=C56)C5=CC=CC=C54)=CC=C3)C=C3OC4=CC=CC(C5=C6C=CC=CC6=C(C6=CC=CC=C6)C6=CC=CC=C65)=C4C3=C2)C(O[H])=C1O[H]'}, 'PubChem-163618539': {'score': -13.95203, 'rmsd': 3.47923, 'smiles': '[H]OC1=CC2=C(C3=C(O[H])C(O[H])=C(O[H])C(O[H])=C3O[H])C3=CC(O[H])=C(O[H])C=C3C(C3=C4C(=C(O[H])C(O[H])=C3O[H])OC3=C(O[H])C(O[H])=C(O[H])C(O[H])=C34)=C2C=C1O[H]'}, 'ZINC000257529314 257529314 PubChem-125039952': {'score': -13.9045, 'rmsd': 2.12111, 'smiles': '[H]OCC1OC(OC2C(O[H])C(CO[H])OC(OC3CCC4(C)C(=CCC5C4CCC4(C)C5CC5OC6(CCC(C)CN6[H])C(C)C54)C3)C2O[H])C(OC2OC(C)C(O[H])C(O[H])C2O[H])C(O[H])C1O[H]'}, 'PubChem-145070942': {'score': -13.84629, 'rmsd': 5.08897, 'smiles': '[H]OC1=C(F)C(C(O[H])(O[H])N([H])C2=C(O[H])C(O[H])=C(O[H])C3=C2C(O[H])(O[H])N(C2CCC(=O)N([H])C2=O)C3=O)=C(O[H])C(C(O[H])(O[H])N2C(O[H])(O[H])C(O[H])(O[H])OC(O[H])(O[H])C2(O[H])O[H])=C1'}, 'PubChem-166019899': {'score': -13.83798, 'rmsd': 2.48083, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1)C(O[H])=C1OC3=C(O[H])C(O[H])=C(C4=C5C(O[H])=C(O[H])C(O[H])=C(O[H])C5=C(C5=C(O[H])C(O[H])=C(C6=C(O[H])C(O[H])=C(O[H])C7=C6C(O[H])=C(O[H])C(O[H])=C7O[H])C6=C5C(O[H])=C(O[H])C(O[H])=C6O[H])C5=C(O[H])C(O[H])=C(O[H])C(O[H])=C54)C(O[H])=C3C1=C2O[H]'}, 'PubChem-160864666': {'score': -13.82062, 'rmsd': 5.38553, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])(N([H])[H])C3=C4C(O[H])=C(O[H])C(O[H])=C3O[H])=C(O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C12'}, 'PubChem-163805299': {'score': -13.82005, 'rmsd': 3.50766, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C3OC4=C(C(O[H])=C(O[H])C5=C4C(O[H])=C(O[H])C(O[H])=C5O[H])C3=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(C2=C(O[H])C(O[H])=C(O[H])C3=C2C(O[H])=C(O[H])C(O[H])=C3O[H])=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-163555839': {'score': -13.81021, 'rmsd': 1.94493, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])=C(O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C3=C(O[H])C(O[H])=C(O[H])C(O[H])=C3N([H])C2=C(O[H])C(O[H])=C1O[H]'}, 'PubChem-164006892': {'score': -13.80233, 'rmsd': 1.92979, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C(C3=C(O[H])C(O[H])=C(O[H])C4=C3C(O[H])=C(O[H])C(O[H])=C4O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(O[H])=C(O[H])C2=C1C(O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-156175345': {'score': -13.74367, 'rmsd': 5.11781, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C(C3=C4C(O[H])=C(O[H])C5=C(O[H])C(O[H])=C(O[H])C6=C(O[H])C(O[H])=C(C(O[H])=C3O[H])C4=C56)=C(O[H])C(C3=C4C(O[H])=C(O[H])C5=C(O[H])C(O[H])=C(O[H])C6=C(O[H])C(O[H])=C(C(O[H])=C3O[H])C4=C56)=C2O[H])C(O[H])=C1O[H]'}, 'PubChem-157143405 PubChem-157143409 PubChem-160727519': {'score': -13.72765, 'rmsd': 2.51824, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(O[H])=C3OC4=C(O[H])C5=C(C(O[H])=C(O[H])C(O[H])=C5O[H])C(O[H])=C4C3=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C(O[H])C(O[H])=C(C2=C(O[H])C(O[H])=C(O[H])C3=C2C(O[H])=C(O[H])C(O[H])=C3O[H])C2=C1C(O[H])=C(O[H])C(O[H])=C2O[H]'}, 'PubChem-157143406': {'score': -13.65999, 'rmsd': 5.58489, 'smiles': '[H]OC1=C(O[H])C(O[H])=C(C2=C(O[H])C(O[H])=C(O[H])C(O[H])=C2C2=C3C(O[H])=C(O[H])C(O[H])=C(O[H])C3=C(C3=C(O[H])C(O[H])=C4OC5=C(O[H])C6=C(C(O[H])=C(O[H])C(O[H])=C6O[H])C(O[H])=C5C4=C3O[H])C3=C(O[H])C(O[H])=C(O[H])C(O[H])=C32)C(O[H])=C1O[H]'}, 'PubChem-164033822': {'score': -13.56906, 'rmsd': 2.39568, 'smiles': '[H]OC1=C(O[H])C2=C(C(C3=C(O[H])C(O[H])=C(C4=C5C(O[H])=C(O[H])C(O[H])=C(O[H])C5=C(C5=C(O[H])C6=C(C(O[H])=C(O[H])C(O[H])=C6O[H])C(O[H])=C5O[H])C5=C(O[H])C(O[H])=C(O[H])C(O[H])=C54)C(O[H])=C3O[H])=C1C=C)C1=C(O[H])C(O[H])=C(O[H])C(O[H])=C1O2'}, 'PubChem-157541209': {'score': -13.5311, 'rmsd': 5.49026, 'smiles': '[H]OC(=O)CC1C(=O)N([H])C(C(C)O[H])C(=O)N([H])C(C)C(C(=O)N([H])C(C)(C)C)N2CCCC2C(=O)N([H])C(CC2=CC=C([O+]([H])[H])C=C2)C(=O)N(C)CC(=O)N([H])C(C)C(=O)N1[H]'}, 'PubChem-157541210': {'score': -13.5311, 'rmsd': 5.49026, 'smiles': '[H]OC(=O)CC1C(=O)N([H])C(C(C)O[H])C(=O)N([H])C(C)C(C(=O)N([H])C(C)(C)C)N2CCCC2C(=O)N([H])C(CC2=CC=C(O[H])C=C2)C(=O)N(C)CC(=O)N([H])C(C)C(=O)N1[H]'}, 'PubChem-91604651': {'score': -13.49914, 'rmsd': 4.72934, 'smiles': '[H]OC1=C(OC(O[H])(O[H])O[H])C(OC2C(O[H])(O[H])C(O[H])(O[H])C(O[H])(O[H])C2(O[H])O[H])=C(O[H])C(C2(O[H])CCOCN([H])C2(O[H])O[H])=C1O[H]'}, 'PubChem-163513922': {'score': -13.46967, 'rmsd': 2.87044, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])OC1=C(O[H])C(C3=C4C(O[H])=C(O[H])C(O[H])=C(O[H])C4=C(C4=C(O[H])C(O[H])=C(C5=C6C(=C(O[H])C(O[H])=C5O[H])OC5=C(O[H])C(O[H])=C(O[H])C(O[H])=C56)C(O[H])=C4O[H])C4=C(O[H])C(O[H])=C(O[H])C(O[H])=C43)=C(O[H])C(O[H])=C12'}, 'PubChem-163468243': {'score': -13.45561, 'rmsd': 3.06115, 'smiles': '[H]OC1=C(O[H])C(O[H])=C2C(=C1O[H])C(C1=C(O[H])C(C3=C(O[H])C(O[H])=C(O[H])C4=C5C(O[H])=C(O[H])C(O[H])=C(O[H])C5=C(O[H])C(O[H])=C34)=C(O[H])C(O[H])=C1O[H])=C1C(O[H])=C(O[H])C(O[H])=C(O[H])C1=C2C1=C2C(=C(O[H])C(O[H])=C1O[H])OC1=C(O[H])C3=C(C(O[H])=C(O[H])C(O[H])=C3O[H])C(O[H])=C12'}}
    run_admet_request(dict_final, "/home/kdunorat/PycharmProjects/LambdaPipe/files/testedefinitivo")