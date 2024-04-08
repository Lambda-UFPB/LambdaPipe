import subprocess
import pandas as pd
import time
import json
from sklearn.preprocessing import MinMaxScaler

# fpadmet_path = importlib.resources.files('pharmisa.fpadmet')
# script_path = fpadmet_path.joinpath('runadmet.sh')
# predicted_fpadmet = str(fpadmet_path.joinpath('/RESULTS/predicted.txt'))


def create_fpadmet_input_file(dict_final, output_folder_path):
    smi_input_file_path = f'{output_folder_path}/fpadmet_smiles.smi'
    with open(smi_input_file_path, 'w') as smi_f:
        for i, key in enumerate(dict_final, start=1):
            smiles = dict_final[key]['smiles']
            smi_f.write(f'{smiles}\tG{str(i).zfill(5)}\n')
    return smi_input_file_path


def get_fpadmet_score(df):
    tox_to_number = {
        'Predicted_4': {'active': 1, 'inactive': 0},
        'Predicted_6': {'EPA1': 1, 'EPA2': 0.75, 'EPA3': 0.5, 'EPA4': 0},
        'Predicted_7': {'P': 1, 'N': 0},
        'Predicted_8': {'P': 1, 'N': 0},
        'Predicted_10': {'Positive': 1, 'Negative': 0},
        'Predicted_17': {'Positive': 1, 'Negative': 0},
        'Predicted_25': {'Yes': 1, 'No': 0},
        'Predicted_29': {'Carcinogen': 1, 'NonCarcinogen': 0},
        'Predicted_35': {'Yes': 1, 'No': 0},
        'Predicted_40': {'P': 1, 'N': 0}
    }
    all_columns = df.columns
    tox_columns = [col for col in all_columns if 'Predicted' in col]
    for col in tox_columns:
        df[col] = df[col].map(tox_to_number[col])
    df['FPADMET_Score'] = df[tox_columns].sum(axis=1)
    df = df.sort_values('FPADMET_Score', ascending=True)
    df = df.head(3500)
    df.to_csv('fpadmet_results_sorted.csv')
    return df


def get_new_dict_final(dict_final, smi_input_file, fpadmet_df):
    smiles_dict = {}
    with open(smi_input_file, 'r') as f:
        for line in f:
            smiles, code = line.strip().split('\t')
            smiles_dict[code] = smiles

    smiles_list = []
    for code in fpadmet_df['Molecule']:
        smiles = smiles_dict.get(code)
        if smiles is not None:
            smiles_list.append(smiles)

    for key in dict_final.copy():
        if dict_final[key]['smiles'] not in smiles_list:
            dict_final.pop(key)

    return dict_final


def run_loop_fpadmet(fpadmet_path, script_path, smi_input_file, tox_parameters):
    results = []
    parameter_names = {
        4: 'AMES Mutagenecity',
        6: 'Rat Acute LD50',
        7: 'Drug-Induced Liver Inhibition',
        8: 'HERG Cardiotoxicity',
        10: 'Myelotoxicity',
        17: 'Myopathy Toxicity',
        25: 'Respiratory Toxicity',
        29: 'Carcinogenecity',
        35: 'Ototoxicity',
        40: 'Cytotoxicity HepG2 cell line',
    }
    for parameter in tox_parameters:
        print(f'Running fpadmet for {parameter_names[parameter]}')
        command = ["bash", script_path, "-f", smi_input_file, "-p", str(parameter)]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        predicted_fpadmet = f'{fpadmet_path}/RESULTS/predicted{parameter}.txt'
        df_temp = pd.read_csv(predicted_fpadmet, sep=' ', header=None, names=['Molecule', f'Predicted_{parameter}'])
        df_temp.set_index('Molecule', inplace=True)  # Set 'Molecule' as index
        results.append(df_temp)
    df = pd.concat(results, axis=1)
    df.reset_index(inplace=True)
    df = df.iloc[1:]
    df.to_csv('fpadmet_results.csv')
    return df


def run_fpadmet(dict_final, output_folder_path):
    fpadmet_path = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet'
    script_path = f'{fpadmet_path}/runadmet.sh'
    #smi_input_file = create_fpadmet_input_file(dict_final, output_folder_path)
    smi_input_file = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet-backup/mols.smi'
    tox_parameters = [4, 6, 7, 8, 10, 17, 25, 29, 35, 40]
    fpadmet_df = run_loop_fpadmet(fpadmet_path, script_path, smi_input_file, tox_parameters)
    fpadmet_df = get_fpadmet_score(fpadmet_df)
    dict_final = get_new_dict_final(dict_final, smi_input_file, fpadmet_df)

    return dict_final


if __name__ == '__main__':
    start = time.time()
    with open('dict_final.json', 'r') as file:
        dict_final_teste = eval(file.read())
    output_folder_path1 = '/home/kdunorat/lambdapipe_results/7KR1-3-CID87'
    dict_final1 = run_fpadmet(dict_final_teste, output_folder_path1)
    with open('dict_final_fpadmet.json-teste', 'w') as file:
        file.write(json.dumps(dict_final1))
    end = time.time()
    print(f'Time elapsed: {end - start} seconds')
