import pandas as pd
from utils import create_folder


class AdmetAnalyzer:
    def __init__(self, csv_path: str, admet_path: str, best_molecules_dict: dict, dict_smiles_list: list):
        self.admet_df = pd.read_csv(csv_path)
        self.admet_path = admet_path
        self.results_path = create_folder('results')
        self.best_molecules_dict = best_molecules_dict
        self.dict_smiles_list = dict_smiles_list
        self.admet_df['smiles'] = self.dict_smiles_list

    def _filter_toxicity(self):
        first_column = self.admet_df.iloc[:, 0]
        lipinski = self.admet_df.loc[:, 'Lipinski']
        columns_27_to_38 = self.admet_df.iloc[:, 27:38]

        self.admet_df = pd.concat([first_column, columns_27_to_38, lipinski], axis=1)

    def _filter_conditions(self):
        condition1 = (self.admet_df.select_dtypes(include=['float64']) > 0.3).sum(axis=1) <= 3
        condition2 = self.admet_df['Lipinski'] == 'Accepted'
        condition3 = self.admet_df['Respiratory'] <= 0.3
        combined_condition = condition1 & condition2 & condition3

        self.admet_df = self.admet_df[combined_condition]

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
        self.admet_df['Score'] = score
        self.admet_df['RMSD'] = rmsd
        cols = ['Molecule ID'] + [col for col in self.admet_df if col != 'Molecule ID']
        self.admet_df = self.admet_df[cols]

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

    def run_admet_analyzer(self, output_name: str):
        self._filter_toxicity()
        self._filter_conditions()
        self._get_molecule_id()
        self._get_score_and_rmsd()
        category_df = self.admet_df.select_dtypes(include=['float64']).map(AdmetAnalyzer._generate_category_df)
        for column in category_df.columns:
            self.admet_df[column] = self.admet_df[column].astype(object)
        self.admet_df.update(category_df)
        if not output_name:
            output_name = 'admet_filtered'
        self.admet_df.to_csv(f'{self.results_path}/{output_name}.csv', index=False)
