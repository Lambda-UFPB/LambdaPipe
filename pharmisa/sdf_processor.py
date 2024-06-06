from utils import *
from rdkit import RDLogger, Chem
from tqdm import tqdm


class SdfProcessor:
    """Selects the best molecules from sdf files"""
    def __init__(self, minimize_count: int, output_folder_path: str, score: float, cli_rmsd: float):
        self.output_folder_path = output_folder_path
        self.score = score
        self.cli_rmsd = cli_rmsd
        self.minimize_count = minimize_count
        self.sdf_files = []
        self.best_molecules = []
        self.analyzed_mol = set()
        self.smiles_found = []

    def __getitem__(self, index):
        return self.best_molecules[index]

    def get_sdfs(self):
        """Get the .sdfs files from download page"""
        last_files = get_last_files(file_pattern='minimized_results*', minimize_count=self.minimize_count)
        if len(last_files) > self.minimize_count:
            n = len(last_files) - self.minimize_count
            last_files = last_files[:-n]
        for file in last_files:
            transfer_to_folder(file, self.output_folder_path, 'mv')
            file_name = get_file_name(file)
            zipped_path = f"{self.output_folder_path}/{file_name}"
            unzipped_path = unzip(zipped_path)
            self.sdf_files.append(unzipped_path)

    def _process_sdf(self):
        """Generate dict with Molecule ID: (score, smiles)"""
        for file in tqdm(self.sdf_files, desc="Processing Pharmit Results", ncols=100):
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
                    if smiles not in self.smiles_found:
                        self.best_molecules.append((mol_ids, score, rmsd, smiles))
                        self.analyzed_mol = self.analyzed_mol.union(mol_ids_set)
                        self.smiles_found.append(smiles)
                else:
                    continue

    def _mol_check(self, mol_ids_set: set, score: float, rmsd: float) -> bool:
        """Check if the molecule is already in the analyzed_mol
        set and if it fits the threshold (score < input_score and rmsd < input_rmsd)"""
        if not mol_ids_set.intersection(self.analyzed_mol):
            if score < self.score and rmsd <= self.cli_rmsd:
                return True

    def _get_best_molecules_dict(self):
        """Returns a dict with the top best molecules"""
        return {mol[0]: {'score': mol[1], 'rmsd': mol[2], 'smiles': mol[3]} for mol in self.best_molecules}

    def run_sdfprocessor(self):
        self._process_sdf()
        if self.best_molecules:
            write_stats(f"\n\nNumber of molecules after filtering (Score < {self.score} and RMSD < {self.cli_rmsd}): "
                        f"{len(self.best_molecules)}", self.output_folder_path)
            write_stats(f"\nBest score found: {self.best_molecules[0]}", self.output_folder_path)
        else:
            raise ValueError('No molecules that fit the threshold found in the .sdf files')
        
        return self._get_best_molecules_dict()
