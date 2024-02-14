import utils
import os
from rdkit import RDLogger, Chem


class SdfProcessor:
    """Selects the best molecules from sdf files"""
    def __init__(self, minimize_count):
        self.minimize_count = minimize_count
        self.sdf_files = []
        self.best_molecules = []
        self.analyzed_mol = set()
        self.files_path = f"{os.getcwd()}/files"

    def _get_sdfs(self):
        """Get the .sdfs files from download page"""
        last_files = utils.get_last_files('minimized_results*', self.minimize_count)
        if len(last_files) > self.minimize_count:
            n = len(last_files) - self.minimize_count
            last_files = last_files[:-n]

        for file in last_files:
            utils.transfer_to_folder(file, self.files_path, 'cp')
            file_name = utils.get_file_name(file)
            zipped_path = f"{self.files_path}/{file_name}"
            unzipped_path = utils.unzip(zipped_path)
            self.sdf_files.append(unzipped_path)

        return last_files
    
    def _extract_sdf_files(self, last_files: list):
        """Extracts the .sdf files from the .gz files"""
        for file in last_files:
            utils.transfer_to_folder(file, self.files_path, 'mv')
            file_name = utils.get_file_name(file)
            zipped_path = f"{self.files_path}/{file_name}"
            unzipped_path = utils.unzip(zipped_path)
            self.sdf_files.append(unzipped_path)

    def _process_sdf(self):
        """Generate dict with Molecule ID: (score, smiles)"""

        for file in self.sdf_files:
            lg = RDLogger.logger()
            lg.setLevel(RDLogger.CRITICAL)  # Suppresses RDKit warnings
            mol_supplier = Chem.SDMolSupplier(file, strictParsing=True, sanitize=False)
            for index, mol in enumerate(mol_supplier):
                try:
                    mol_ids = mol.GetProp("_Name")
                    mol_ids_set = {i for i in mol_ids.split(' ')}
                except AttributeError:
                    continue
                score = float(mol.GetProp("minimizedAffinity"))
                rmsd = float(mol.GetProp("minimizedRMSD"))
                if self._mol_check(mol_ids_set, score, rmsd):
                    smiles = Chem.MolToSmiles(mol, isomericSmiles=False)
                    self.best_molecules.append((mol_ids, score, rmsd, smiles))
                    self.analyzed_mol = self.analyzed_mol.union(mol_ids_set)

    def _get_top_molecules(self, top: int):
        """Get the top 50 molecules"""
        self.best_molecules.sort(key=lambda x: x[1], reverse=True)
        self.best_molecules = self.best_molecules[:top]
    
    def _mol_check(self, mol_ids_set: set, score: float, rmsd: float) -> bool:
        """Check if the molecule is already in the analyzed_mol
        set and if it fits the threshold (score < -11 and rmsd < 7)"""
        if not mol_ids_set.intersection(self.analyzed_mol):
            if score < -11 and rmsd < 7:
                return True

    def _get_best_molecules_dict(self):
        """Returns a dict with the top best molecules"""
        return {mol[0]: {'score': mol[1], 'rmsd': mol[2], 'smiles': mol[3]} for mol in self.best_molecules}

    def run_sdfprocessor(self, top: int):
        last_files = self._get_sdfs()
        self._extract_sdf_files(last_files)
        self._process_sdf()
        if self.best_molecules:
            
            if len(self.best_molecules) > top:
                self._get_top_molecules(top)
            else:
                raise ValueError(f'No sufficient molecules ({top}) to fit the threshold found')
        else:
            raise ValueError('No molecules that fit the threshold found')
        
        return self._get_best_molecules_dict()


if __name__ == '__main__':
    sdf = SdfProcessor(10)
    dict_final = sdf.run(50)
    print(dict_final)
