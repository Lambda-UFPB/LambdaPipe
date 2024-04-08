
import subprocess
import pandas as pd
import multiprocessing as mp
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


def run_command(args):
    parameter, script_path, input_file, fpadmet_path = args
    command = ["bash", script_path, "-f", input_file, "-p", str(parameter)]
    # subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(command)


def get_fpadmet_results(smi_input_file_path, num_cores=None):
    if not num_cores:
        num_cores = mp.cpu_count()
        num_cores = num_cores - 1 if num_cores > 1 else 1
    cores_to_show = num_cores if num_cores < 10 else 10
    print(f'Performing FPADMET analysis with {cores_to_show} cores...')
    #tox_parameters = [4, 6, 7, 8, 11, 17, 25, 29, 40, 56]
    tox_parameters = [25, 29]

    fpadmet_path = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet'
    script_path = f'{fpadmet_path}/runadmet.sh'
    #input_file = smi_input_file_path
    input_file = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet/mols.smi'


    args = [(parameter, script_path, input_file, fpadmet_path) for parameter in tox_parameters]

    with mp.Pool(num_cores) as pool:
        pool.map(run_command, args)

    df = create_dataframe(fpadmet_path, tox_parameters)

    return df


def create_dataframe(fpadmet_path, tox_parameters):
    results = []
    for parameter in tox_parameters:
        predicted_fpadmet = f'{fpadmet_path}/RESULTS/predicted{parameter}.txt'
        df_temp = pd.read_csv(predicted_fpadmet, sep=' ', header=None, names=['Molecule', f'Predicted_{parameter}'])
        df_temp.drop_duplicates(subset='Molecule', keep='first', inplace=True)
        df_temp.set_index('Molecule', inplace=True)
        results.append(df_temp)

    df = pd.concat(results, axis=1)
    df.to_csv('fpadmet_results.csv')
    return df


def run_one_each_time(input_smiles):
    results = []
    fpadmet_path = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet'
    script_path = f'{fpadmet_path}/runadmet.sh'
    input_file = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet/mols.smi'
    tox_parameters = [25, 29]
    for parameter in tox_parameters:
        command = ["bash", script_path, "-f", input_file, "-p", str(parameter)]
        subprocess.run(command)
        predicted_fpadmet = f'{fpadmet_path}/RESULTS/predicted{parameter}.txt'
        df_temp = pd.read_csv(predicted_fpadmet, sep=' ', header=None, names=['Molecule', f'Predicted_{parameter}'])
        df_temp.drop_duplicates(subset='Molecule', keep='first', inplace=True)
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
    smi_input_file = create_fpadmet_input_file(dict_final_teste, output_folder_path)
    input_smiles = '/home/kdunorat/Projetos/PharMisa/pharmisa/fpadmet/mols.smi'
    #fpadmet_df = get_fpadmet_results(smi_input_file)
    fpadmet_df = run_one_each_time(input_smiles)
    end = time.time()
    print(f'Time elapsed: {end - start} seconds')

