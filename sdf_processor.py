import utils
import os
from rdkit import Chem
import timeit
import json

class SdfProcessor:
    """Selects the best molecules from sdf files"""
    def __init__(self, minimize_count):
        self.minimize_count = minimize_count
        self.sdf_files = []
        self.best_molecules = dict()

    def _get_sdfs(self):
        """Get the .sdfs files from download page"""
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
        """Generate dict with Molecule ID: (score, smiles)"""
        analyzed_mol = set()
        for file in self.sdf_files:
            mol_supplier = Chem.SDMolSupplier(file, strictParsing=True, sanitize=False)
            for index, mol in enumerate(mol_supplier):
                try:
                    mol_ids = mol.GetProp("_Name")
                    mol_ids_set = {i for i in mol_ids.split(' ')}
                except AttributeError:
                    continue
                score = float(mol.GetProp("minimizedAffinity"))
                if self._mol_check(mol_ids_set, analyzed_mol, score):
                    smiles = Chem.MolToSmiles(mol, isomericSmiles=False)
                    self.best_molecules[mol_ids] = (score, smiles)
                    analyzed_mol = analyzed_mol.union(mol_ids_set)
        return self.best_molecules
    
    @staticmethod
    def _create_final_json(best_mol_dict: dict):
        with open('LastResults.json', 'w') as lr:
            json.dump(best_mol_dict, lr)
            
        
        

    @staticmethod
    def _mol_check(mol_ids_set: set, analyzed_mol: set, score: float) -> bool:
        if not mol_ids_set.intersection(analyzed_mol):
            if score < -10:
                return True

    def run(self):
        self._get_sdfs()
        best_molecules = self._process_sdf()
        SdfProcessor._create_final_json(best_molecules)


if __name__ == '__main__':
    sdf = SdfProcessor(1)
    execution_time = timeit.timeit(sdf.run, number=1)
    print(execution_time)
