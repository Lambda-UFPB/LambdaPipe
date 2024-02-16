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
from utils import get_absolute_path, merge_csv
import time


@click.command()
@click.argument("receptor_file", type=click.Path(exists=True), required=True)
@click.argument("ligand_file", type=click.Path(exists=True), required=True)
@click.option("--top", type=int, default=50, help="The number of the top molecules by score to search in admetlab 2.0")
@click.option("--rmsd", type=float, default=7.0, help="RMSD threshold for filtering the results")
@click.option("--pharma", is_flag=True, help="Prompt the user for additional input")
@click.option("--output", type=click.Path(), help="Output file for the final results")
def lambdapipe(receptor_file, ligand_file, top, rmsd, pharma, output):
    phc = PharmitControl(get_absolute_path(receptor_file), get_absolute_path(ligand_file))
    phc.upload_complex()
    phc.get_json()
    jsh = JsonHandler()
    if pharma:
        while True:
            click.echo(phc.show_pharmacophore_menu(jsh.session))
            switch = click.prompt("Pharmacophore feature number that you want to switch "
                                  "(Enter 0 to start search with the current features)", type=int)
            time.sleep(2)
            if switch == 0:
                break
            else:
                jsh.pharma_switch(switch)

    modified_json_path = jsh.create_json()
    click.echo("Starting pharmit search...")
    minimize_count = phc.run_pharmit_search(modified_json_path)
    click.echo("Processing Results...")
    sdfp = SdfProcessor(minimize_count, top, rmsd)
    dict_final = sdfp.run_sdfprocessor()
    click.echo("Getting ADMET info...")
    smiles_list, admet_folder = run_admet_request(dict_final)
    merge_csv(admet_folder)
    click.echo("Generating final results...")
    analyzer = AdmetAnalyzer(f'{admet_folder}/merged.csv', admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer(output)
    click.echo("Go to the results folder to see the final results")


"""
def run_pharmit():
    phc = PharmitControl()
    minimize_count = phc.run_pharmit_control()
    sdfp = SdfProcessor(minimize_count)
    dict_final = sdfp.run_sdfprocessor(50)
    smiles_list, admet_folder = run_admet_request(dict_final)
    merge_csv(admet_folder)
    analyzer = AdmetAnalyzer(f'{admet_folder}/merged.csv', admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer()

"""


if __name__ == "__main__":
    start_time = time.time()
    lambdapipe()
    end_time = time.time()
    print(f"Total time: {end_time - start_time}")
