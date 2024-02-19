"""
LambdaPipe is a program that uses the pharmit webserver  and admetlab 2.0 in an integrated pipeline to find
the best molecules for a given target.

Author: Carlos Eduardo Norat
Github: https://github.com/kdunorat
Email: kdu.norat@gmail.com

"""

import click
from pharmit_control import PharmitControl
from json_handler import JsonHandler
from sdf_processor import SdfProcessor
from admet_request import run_admet_request
from admet_analyzer import AdmetAnalyzer
from utils import (generate_folder_name, create_folders, create_stats_file, get_download_list, get_absolute_path,
                   merge_csv)
import time


@click.command()
@click.argument("receptor_file", type=click.Path(exists=True), required=True)
@click.argument("ligand_file", type=click.Path(exists=True), required=True)
@click.option("-t", "--top", type=int, default=50, help="The number of the top molecules by score to search in admetlab 2.0")
@click.option("-r", "--rmsd", type=float, default=7.0, help="RMSD threshold for filtering the results")
@click.option("-p", "--pharma", is_flag=True, help="Prompt the user for additional input")
@click.option("-o", "--output", type=click.Path(), help="Folder name containing the results")
def lambdapipe(receptor_file, ligand_file, top, rmsd, pharma, output):
    start_time = time.time()
    folder_name = output if output else generate_folder_name()
    output_folder_path = create_folders(folder_name)
    create_stats_file(output_folder_path)
    admet_folder = f"{output_folder_path}/admet"
    old_download_list = get_download_list('pharmit*.json*')

    phc = PharmitControl(get_absolute_path(receptor_file), get_absolute_path(ligand_file), output_folder_path)
    phc.upload_complex()
    phc.get_json()
    jsh = JsonHandler(output_folder_path, old_download_list)

    if pharma:
        while True:
            click.echo(jsh)
            switch = click.prompt("Pharmacophore feature number that you want to switch "
                                  "(Enter 0 to start search with the current features)", type=int)
            time.sleep(1)
            if switch == 0:
                break
            else:
                jsh.pharma_switch(switch)
    modified_json_path = jsh.create_json()

    click.echo("Starting pharmit search...")
    minimize_count = phc.run_pharmit_search(modified_json_path)
    click.echo("\nProcessing Results...")
    sdfp = SdfProcessor(minimize_count, top, output_folder_path, rmsd)
    dict_final = sdfp.run_sdfprocessor()

    click.echo("\nGetting ADMET info...")
    smiles_list = run_admet_request(dict_final, output_folder_path)
    merge_csv(admet_folder)

    click.echo("\nGenerating final results...")
    analyzer = AdmetAnalyzer(output_folder_path, admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer()
    click.echo(f"\nGo to the {folder_name} directory in files to see the final results")
    elapsed_time = time.time()
    click.echo(f"Total time: {elapsed_time - start_time}")


if __name__ == "__main__":
    lambdapipe()
