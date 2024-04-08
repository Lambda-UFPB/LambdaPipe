from .utils import *


class AdmetAnalyzer:
    def __init__(self, output_folder_path: str, best_molecules_dict: dict, list_mol: list):
        self.output_folder_path = output_folder_path
        self.admet_df = pd.DataFrame(list_mol)
        self._selected_columns()
        self.admet_df = self.admet_df.rename(columns={'id': 'Molecule ID', 'smiles': 'SMILES', 'Synth': 'SA-score'})
        self.results_path = f"{output_folder_path}/results"
        self.best_molecules_dict = best_molecules_dict

    def _selected_columns(self):
        all_columns = self.admet_df.columns.tolist()
        final_columns = ['id']
        metabolism = all_columns[54:68]
        excretion = all_columns[68:70]
        distribution = all_columns[45:54]
        absortion = all_columns[36:45]
        medicinal = all_columns[15:29]
        medicinal_2 = ['Aggregators', 'Fluc',
                       'Blue_fluorescence', 'Green_fluorescence', 'Reactive', 'Promiscuous']
        medicinal.extend(medicinal_2)
        toxi_rules = ['NonBiodegradable', 'NonGenotoxic_Carcinogenicity', 'SureChEMBL', 'Skin_Sensitization',
                      'Acute_Aquatic_Toxicity',
                      'Toxicophores', 'Genotoxic_Carcinogenicity_Mutagenicity']
        toxicity = all_columns[70:94]
        tox21 = all_columns[94:106]
        smiles = all_columns[0]
        final_columns.extend(medicinal)
        final_columns.extend(absortion)
        final_columns.extend(distribution)
        final_columns.extend(metabolism)
        final_columns.extend(excretion)
        final_columns.extend(toxi_rules)
        final_columns.extend(toxicity)
        final_columns.extend(tox21)
        final_columns.append(smiles)
        self.admet_df = self.admet_df[final_columns]

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

    def run_admet_analyzer(self):
        self._get_score_and_rmsd()
        best_score = self.admet_df['Score Pharmit'].min()
        num_molecules = self.admet_df.shape[0]
        write_stats(f"\n\nNumber of molecules after admet filter: {num_molecules}\n"
                    f"Best score after admet research: {best_score}", self.output_folder_path)

        self.admet_df.to_csv(f'{self.results_path}/admet_filtered.csv', index=False)
