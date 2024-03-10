"""
LambdaPipe is a program that uses the pharmit webserver  and admetlab 2.0 in an integrated pipeline to find
the best molecules for a given target.

Author: Carlos Eduardo Norat
Github: https://github.com/kdunorat
Email: kdu.norat@gmail.com

"""

import click
import time
import asyncio
from pharmit_control import PharmitControl
from top_feature_configs import run_feature_configs
from pharma_optimizer import PharmaOptimizer
from json_handler import JsonHandler
from sdf_processor import SdfProcessor
from admet_request import run_admet_request
from admet_analyzer import AdmetAnalyzer
from get_html import results_to_html
from utils import (generate_folder_name, create_folders, create_stats_file, get_download_list,
                   get_absolute_path, write_stats, merge_csv)



@click.command()
@click.argument("receptor_file", type=click.Path(exists=True), required=False)
@click.argument("ligand_file", type=click.Path(exists=True), required=False)
@click.option("-t", "--top", type=int, default=300,
              help="The number of the top molecules by score to search in admetlab 2.0")
@click.option("-r", "--rmsd", type=float, default=7.0, help="RMSD threshold for filtering the results")
@click.option("-p", "--pharma", is_flag=True, help="Prompt the user for additional input")
@click.option("-s", "--session", type=str, help="Session file for pharmit search")
@click.option("--plip_csv", type=str, help="PLIP csv file for optimized pharmit search")
@click.option("-f", "--fast", is_flag=True, help="Perform all the databases search in the same browser window")
@click.option("-o", "--output", type=click.Path(), help="Folder name containing the results")
def lambdapipe(receptor_file, ligand_file, top, rmsd, pharma, session, plip_csv, fast, output):
    if (not session and (not receptor_file or not ligand_file)) or (session and (receptor_file or ligand_file)):
        raise click.BadParameter(
            "You must provide either a session or both a receptor file and a ligand file.")
    if (plip_csv and session) or (plip_csv and pharma):
        raise click.BadParameter(
            "You can't provide a plip csv file with a session or with the pharma flag.")

    start_time = time.time()
    folder_name = output if output else generate_folder_name()
    try:
        output_folder_path, admet_folder, old_download_list = create_folder(folder_name)
    except FileExistsError:
        click.echo(f"The folder {folder_name} already exists. Please provide a different name.")
        return
    pharmacophore_number = None
    if session:
        phc = PharmitControl('', '', output_folder_path)
        new_session = session

    else:
        jsh, phc = creating_complex(receptor_file, ligand_file, output_folder_path, old_download_list)
        if pharma:
            pharmacophore_selection_menu(jsh)
            new_session = [jsh.create_json()]

        elif plip_csv:
            popt = PharmaOptimizer(jsh.session, plip_csv)
            pharmit_spheres_list = popt.run_pharma_optimizer()
            configs_list = run_feature_configs(pharmit_spheres_list)
            new_session = []
            for index, config in enumerate(configs_list):
                jsh.write_points(config)
                new = jsh.create_json(file_index=index+1)
                new_session.append(new)
                pharmacophore_number = len(jsh.session["points"])
        else:
            new_session = [jsh.create_json()]

    exec_lambdapipe(new_session, phc, top, output_folder_path, admet_folder, rmsd, folder_name, start_time,
                        pharmacophore_number, fast)


def exec_lambdapipe(new_session, phc, top, output_folder_path, admet_folder, rmsd, folder_name, start_time,
                        pharmacophore_number, fast=False):
    minimize_count = 0
    quit_now = False
    for index, session in enumerate(reversed(new_session)):
        click.echo(f"Starting pharmit search of config {index + 1}")
        if index == len(session) - 1:
            quit_now = True
        print(f"quit_now = {quit_now}")
        if pharmacophore_number:
            write_stats(f"Results with {pharmacophore_number} pharmacophores:\n", output_folder_path)
            pharmacophore_number -= 1
        minimize_count += phc.run_pharmit_search(session, run_lambdapipe=index, quit_now=quit_now, fast=fast)
        print(f"minimize count = {minimize_count}")
        phc.no_results = []
        phc.minimize_count = 0

    click.echo("\nProcessing Results...")
    sdfp = SdfProcessor(minimize_count, top, output_folder_path, rmsd)
    dict_final = sdfp.run_sdfprocessor()

    click.echo("\nGetting ADMET info...")
    smiles_list = asyncio.run(asyncio.wait_for(run_admet_request(dict_final, output_folder_path), timeout=1200))
    merge_csv(admet_folder)

    click.echo("\nGenerating final results...")
    analyzer = AdmetAnalyzer(output_folder_path, admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer()
    results_to_html(output_folder_path, folder_name)

    click.echo(f"\nGo to {output_folder_path} to see the final results")
    elapsed_time = time.time()
    click.echo(f"\n\nAnalysis Completed\n{(elapsed_time - start_time)/60:.2f} minutes")


def create_folder(folder_name):
    output_folder_path = create_folders(folder_name)
    create_stats_file(output_folder_path)
    admet_folder = f"{output_folder_path}/admet"
    old_download_list = get_download_list('pharmit*.json*')

    return output_folder_path, admet_folder, old_download_list


def creating_complex(receptor_file, ligand_file, output_folder_path, old_download_list):
    phc = PharmitControl(get_absolute_path(receptor_file), get_absolute_path(ligand_file), output_folder_path)
    phc.upload_complex()
    phc.get_json()
    jsh = JsonHandler(output_file_path=output_folder_path, old_download_list=old_download_list)

    return jsh, phc


def pharmacophore_selection_menu(jsh):
    while True:
        click.echo(jsh)
        switch = click.prompt("Pharmacophore feature number that you want to switch "
                              "(Enter 0 to start search with the current features)", type=int)
        time.sleep(1)
        if switch == 0:
            break
        else:
            jsh.pharma_switch(switch)


if __name__ == "__main__":
    lambdapipe()
