from utils import *
from exceptions import NoMoleculeError


class AdmetAnalyzer:
    def __init__(self, output_folder_path: str, admet_path: str, best_molecules_dict: dict, dict_smiles_list: list):
        csv_path = f'{admet_path}/merged.csv'
        self.output_folder_path = output_folder_path
        self.admet_df = pd.read_csv(csv_path)
        self.admet_path = admet_path
        self.results_path = f"{output_folder_path}/results"
        self.best_molecules_dict = best_molecules_dict
        self.dict_smiles_list = dict_smiles_list
        self.admet_df['smiles'] = self.dict_smiles_list

    def _filter_toxicity(self):
        first_column = self.admet_df.iloc[:, 0]
        lipinski = self.admet_df.loc[:, 'Lipinski']
        toxicity = self.admet_df.iloc[:, 27:38]
        tox_21pathway = self.admet_df.iloc[:, 42:54]

        self.admet_df = pd.concat([first_column, toxicity, tox_21pathway, lipinski], axis=1)

    def _filter_conditions(self):
        condition1 = (self.admet_df.iloc[:, 27:38].select_dtypes(include=['float64']) > 0.3).sum(axis=1) <= 3
        condition2 = (self.admet_df.iloc[:, 42:54].select_dtypes(include=['float64']) > 0.3).sum(axis=1) <= 3
        condition3 = self.admet_df['Respiratory'] <= 0.3
        combined_condition = condition1 & condition2 & condition3

        self.admet_df = self.admet_df[combined_condition]
        if self.admet_df.empty:
            raise NoMoleculeError("No molecules passed the admet filter")

    def _get_molecule_id(self):
        mol_ids = []
        for smiles_admet in self.admet_df['smiles']:
            for molecule_id, properties in self.best_molecules_dict.items():
                dict_smile = properties['smiles']
                if dict_smile == smiles_admet:
                    mol_ids.append(molecule_id)
        self.admet_df['Molecule ID'] = mol_ids

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
        cols = ['Molecule ID'] + [col for col in self.admet_df if col != 'Molecule ID']
        self.admet_df = self.admet_df[cols]

    @staticmethod
    def _write_best_molecule_after(self):
        best_molecules_df = pd.DataFrame(self.best_molecules_dict).T
        best_molecules_df.to_csv(f'{self.results_path}/best_molecules.csv', index=True)

    @staticmethod
    def _generate_category_df(parameter_value):
        categories = {
            (0.0, 0.1): '---',
            (0.1, 0.3): '--',
            (0.3, 0.5): '-',
            (0.5, 0.7): '+',
            (0.7, 0.9): '++',
            (0.9, 1.0): '+++'
        }
        for (low, high), category in categories.items():
            if parameter_value == 0:
                return '---'
            if low < parameter_value <= high:
                return category

    def run_admet_analyzer(self):
        self._filter_toxicity()
        self._filter_conditions()
        self._get_molecule_id()
        self._get_score_and_rmsd()
        """
        category_df = self.admet_df.select_dtypes(include=['float64']).map(AdmetAnalyzer._generate_category_df)
        for column in category_df.columns:
            self.admet_df[column] = self.admet_df[column].astype(object)
        self.admet_df.update(category_df)
        """
        best_score = self.admet_df['Score'].min()
        num_molecules = self.admet_df.shape[0]
        write_stats(f"\nNumber of molecules after admet filter: {num_molecules}\n"
                    f"Best score after admet research: {best_score}", self.output_folder_path)

        self.admet_df.to_csv(f'{self.results_path}/admet_filtered.csv', index=False)
