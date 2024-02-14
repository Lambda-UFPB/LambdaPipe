"""
LambdaPipe is a program that uses the pharmit webserver  and admetlab 2.0 in an integrated pipeline to find
the best molecules for a given target.

Author: Carlos Eduardo Norat
Github: https://github.com/kdunorat
Email: kdu.norat@gmail.com

"""


from pharmit_control import PharmitControl
from sdf_processor import SdfProcessor
from admet_request import run_admet_request
from admet_analyzer import AdmetAnalyzer
from utils import merge_csv
import timeit


def run_pharmit():
    phc = PharmitControl()
    minimize_count = phc.run_pharmit_control()
    sdfp = SdfProcessor(minimize_count)
    dict_final = sdfp.run_sdfprocessor(50)
    smiles_list, admet_folder = run_admet_request(dict_final)
    merge_csv(admet_folder)
    analyzer = AdmetAnalyzer(f'{admet_folder}/merged.csv', admet_folder, dict_final, smiles_list)
    analyzer.run_admet_analyzer()


if __name__ == '__main__':
    print(timeit.timeit('run_pharmit()', globals=globals(), number=1))
