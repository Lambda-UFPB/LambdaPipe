import subprocess
import pandas as pd
import time

# fpadmet_path = importlib.resources.files('pharmisa.fpadmet')
# script_path = fpadmet_path.joinpath('runadmet.sh')
# predicted_fpadmet = str(fpadmet_path.joinpath('/RESULTS/predicted.txt'))


def create_fpadmet_input_file(dict_final, output_folder_path):
    smi_input_file_path = f'{output_folder_path}/fpadmet_smiles.smi'
    with open(smi_input_file_path, 'w') as f:
        for i, key in enumerate(dict_final, start=1):
            smiles = dict_final_teste[key]['smiles']
            f.write(f'{smiles}\tG{str(i).zfill(5)}\n')
    return smi_input_file_path


def get_fpadmet_score(df):
    all_columns = df.columns
    tox_columns = [col for col in all_columns if 'Predicted' in col]


def run_fpadmet():
    results = []
    fpadmet_path = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet'
    script_path = f'{fpadmet_path}/runadmet.sh'
    smi_input_file = create_fpadmet_input_file(dict_final_teste, output_folder_path)
    #input_file = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet/mols.smi'
    tox_parameters = [4, 6, 7, 8, 11, 17, 25, 29, 40, 56]
    for parameter in tox_parameters:
        print(f'Running fpadmet for parameter {parameter}')
        command = ["bash", script_path, "-f", smi_input_file, "-p", str(parameter)]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        predicted_fpadmet = f'{fpadmet_path}/RESULTS/predicted{parameter}.txt'
        df_temp = pd.read_csv(predicted_fpadmet, sep=' ', header=None, names=['Molecule', f'Predicted_{parameter}'])
        df_temp.set_index('Molecule', inplace=True)
        results.append(df_temp)
    df = pd.concat(results, axis=1)
    df.to_csv('fpadmet_results.csv')
    return df


if __name__ == '__main__':
    start = time.time()
    with open('dict_final.json', 'r') as f:
        dict_final_teste = eval(f.read())
    output_folder_path = '/home/kdunorat/lambdapipe_results/7KR1-3-CID87'
    fpadmet_df = run_fpadmet()
    end = time.time()
    print(f'Time elapsed: {end - start} seconds')

