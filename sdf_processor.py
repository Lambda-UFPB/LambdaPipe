import utils
import os
from rdkit import Chem
import timeit


class SdfProcessor:
    def __init__(self, minimize_count):
        self.minimize_count = minimize_count
        self.sdf_files = []
        self.best_molecules = dict()

    def _get_sdfs(self):
        last_files = utils.get_last_files('minimized_results')
        files_path = f"{os.getcwd()}/files"

        if len(last_files) > self.minimize_count:
            n = len(last_files) - self.minimize_count
            last_files = last_files[:-n]

        for file in last_files:
            utils.transfer_to_folder(file, files_path, 'cp')
            file_name = utils.get_file_name(file)
            zipped_path = f"{files_path}/{file_name}"
            unzipped_path = utils.unzip(zipped_path)
            self.sdf_files.append(unzipped_path)

    def _process_sdf(self):
        analyzed_mol = set()
        sdf_files = ['/home/kdunorat/projetos/LambdaPipe/files/minimized_results (9).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (8).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (7).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (6).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (5).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (4).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (3).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (2).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results (1).sdf', '/home/kdunorat/projetos/LambdaPipe/files/minimized_results.sdf']
        for file in sdf_files:
            mol_supplier = Chem.SDMolSupplier(file)
            for index, mol in enumerate(mol_supplier):
                if index < 5:
                    try:
                        mol_ids = mol.GetProp("_Name")
                        mol_ids_set = {i for i in mol_ids.split(' ')}
                    except AttributeError:
                        continue
                    print(f'{file}-----{mol_ids}')
                    score = float(mol.GetProp("minimizedAffinity"))
                    if self._mol_check(mol_ids_set, analyzed_mol, score):
                        self.best_molecules[mol_ids] = score
                        analyzed_mol = analyzed_mol.union(mol_ids_set)
        print(self.best_molecules)

    @staticmethod
    def _mol_check(mol_ids_set: set, analyzed_mol: set, score: float):
        if not mol_ids_set.intersection(analyzed_mol):
            if score < -12:
                return True

    def run(self):
        #self._get_sdfs()
        self._process_sdf()


if __name__ == '__main__':
    sdf = SdfProcessor(10)
    execution_time = timeit.timeit(sdf.run, number=1)
    print(execution_time/60)
