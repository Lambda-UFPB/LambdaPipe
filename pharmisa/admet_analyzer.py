from .utils import *
from .exceptions import NoMoleculeError


class AdmetAnalyzer:
    def __init__(self, output_folder_path: str, best_molecules_dict: dict, list_mol: list):
        self.output_folder_path = output_folder_path
        columns = ['id', 'smiles', 'hERG', 'DILI', 'Ames', 'ROA', 'FDAMDD', 'SkinSen', 'Carcinogenicity',
                   'EC', 'EI', 'Respiratory', 'H-HT', 'Neurotoxicity-DI', 'Ototoxicity',
                   'Hematotoxicity', 'Nephrotoxicity-DI', 'Genotoxicity', 'NR-AhR', 'NR-AR', 'NR-AR-LBD',
                   'NR-Aromatase', 'NR-ER', 'NR-ER-LBD',
                   'NR-PPAR-gamma', 'SR-ARE', 'SR-ATAD5', 'SR-HSE', 'SR-MMP', 'SR-p53', 'Synth', 'Lipinski', 'Pfizer',
                   'GSK', 'GoldenTriangle']
        self.admet_df = pd.DataFrame(list_mol, columns=columns)
        self.admet_df = self.admet_df.rename(columns={'id': 'Molecule ID', 'smiles': 'SMILES', 'Synth': 'SA-score'})
        self.results_path = f"{output_folder_path}/results"
        self.best_molecules_dict = best_molecules_dict

    def _filter_conditions(self):
        condition1 = (self.admet_df.iloc[:, 1:17].select_dtypes(include=['float64']) > 0.3).sum(axis=1) <= 4
        condition2 = (self.admet_df.iloc[:, 17:29].select_dtypes(include=['float64']) > 0.3).sum(axis=1) <= 6
        condition3 = self.admet_df['Respiratory'] < 0.7
        condition4 = (self.admet_df.iloc[:, 30:].select_dtypes(include=['int64']) > 0).sum(axis=1) >= 1
        combined_condition = condition1 & condition2 & condition3 & condition4

        self.admet_df = self.admet_df[combined_condition]
        if self.admet_df.empty:
            raise NoMoleculeError("No molecules passed the admet filter")

    def _get_score_and_rmsd(self):
        score = []
        rmsd = []
        for molecule_id in self.admet_df['Molecule ID']:
            for key, value in self.best_molecules_dict.items():
                if molecule_id == key:
                    score.append(value['score'])
                    rmsd.append(value['rmsd'])
        self.admet_df['Score Pharmit'] = score
        self.admet_df['RMSD Pharmit'] = rmsd
        self.admet_df['Molecule ID'] = self.admet_df['Molecule ID'].str.split(' ', n=1, expand=True)[0]
        cols = ['Molecule ID'] + [col for col in self.admet_df if col != 'Molecule ID']
        self.admet_df = self.admet_df[cols]

    @staticmethod
    def _write_best_molecule_after(self):
        best_molecules_df = pd.DataFrame(self.best_molecules_dict).T
        best_molecules_df.to_csv(f'{self.results_path}/best_molecules.csv', index=True)

    def run_admet_analyzer(self):
        self._filter_conditions()
        self._get_score_and_rmsd()
        best_score = self.admet_df['Score Pharmit'].min()
        num_molecules = self.admet_df.shape[0]
        write_stats(f"\n\nNumber of molecules after admet filter: {num_molecules}\n"
                    f"Best score after admet research: {best_score}", self.output_folder_path)

        self.admet_df.to_csv(f'{self.results_path}/admet_filtered.csv', index=False)
