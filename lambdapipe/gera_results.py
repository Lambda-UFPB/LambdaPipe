from sdf_processor import SdfProcessor
from admet_request import run_admet_request
from admet_analyzer import AdmetAnalyzer
from get_html import results_to_html
from utils import merge_csv
import asyncio
import time


def exec_lambdapipe_process(minimize_count, top, output_folder_path, admet_folder, rmsd, folder_name, start_time):
    print("\nProcessing Results...")
    sdfp = SdfProcessor(minimize_count, top, output_folder_path, rmsd)
    sdfp.get_sdfs()
    dict_final = sdfp.run_sdfprocessor()

    print("\nGetting ADMET info...")
    smiles_list = asyncio.run(asyncio.wait_for(run_admet_request(dict_final, output_folder_path), timeout=120000))
    merge_csv(admet_folder)

    print("\nGenerating final results...")
    analyzer = AdmetAnalyzer(output_folder_path, admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer()
    results_to_html(output_folder_path, folder_name)

    print(f"\nGo to {output_folder_path} to see the final results")
    elapsed_time = time.time()
    print(f"\n\nAnalysis Completed\n{(elapsed_time - start_time)/60:.2f} minutes")


if __name__ == '__main__':
    minimize_count = 30
    top = 2000
    output_folder_path = "/home/kdunorat/lambdapipe_results/7DK5-272"
    admet_folder = "/home/kdunorat/lambdapipe_results/7DK5-272/admet"
    rmsd = 7
    folder_name = "7DK5-272"
    start_time = time.time()
    exec_lambdapipe_process(minimize_count, top, output_folder_path, admet_folder, rmsd,
                            folder_name, start_time)
