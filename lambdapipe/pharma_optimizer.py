import json
import pandas as pd
from pharma_sphere import PharmaSphere
from json_handler import JsonHandler


class PharmaOptimizer:
    def __init__(self, pharmit_session: str, plip_csv_path: str):
        self.plip_df = pd.read_csv(plip_csv_path)
        self.mean_quantity = self.plip_df['quantidade'].mean()
        self.pharmit_session = pharmit_session
        self.spheres_dict = {
            'Hydrophobic': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'Hydrophobic'},
            'HydrogenDonor': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenAcceptor'},
            'HydrogenAcceptor': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenDonor'},
            'PositiveIon': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'NegativeIon'},
            'NegativeIon': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'PositiveIon'}
        }
        self.pharmit_spheres_type_available = []

    def _generate_pharmit_spheres(self):
        with open(self.pharmit_session, 'r') as file:
            session = json.load(file)
        pharmit_spheres_type_available = []
        for feature in session['points']:
            if feature['name'] == 'InclusionSphere' or feature['name'] == 'Aromatic':
                continue
            if feature['enabled']:
                self.spheres_dict[feature['name']]['enabled'] += 1

            is_donor = self._check_donor(pharmit_feature=feature)

            if feature['name'] not in pharmit_spheres_type_available:
                self.pharmit_spheres_type_available.append(feature['name'])

            self.spheres_dict[feature['name']]['pharmit_spheres'].append(PharmaSphere(feature['x'], feature['y'],
                                                                                      feature['z'], feature['radius'],
                                                                                      feature['name'], is_donor))

    def _generate_plip_spheres(self):
        for index, row in self.plip_df.iterrows():
            if row['type'] in self.pharmit_spheres_type_available and row['quantidade'] > self.mean_quantity:
                is_donor = self._check_donor(plip_row=row)
                plip_interaction_type = self._plip_new_interaction_type(row['type'], is_donor)
                if plip_interaction_type in self.pharmit_spheres_type_available:
                    plip_sphere = PharmaSphere(row['x'], row['y'], row['z'], row['raio'], plip_interaction_type,
                                               is_donor, index=index)
                    plip_sphere.quantity = row['quantidade']
                    self.spheres_dict[plip_interaction_type]['plip_spheres'].append(plip_sphere)

    @staticmethod
    def _check_donor(pharmit_feature: dict = None, plip_row: pd.Series = None):
        if pharmit_feature:
            if 'Donor' in pharmit_feature['name'] or 'Positive' in pharmit_feature['name']:
                donor = True
            else:
                donor = False
        else:
            if pd.isna(plip_row['protis']):
                donor = None
            else:
                donor = plip_row['protis']

        return donor

    @staticmethod
    def _plip_new_interaction_type(row_type: str, is_donor: bool):
        if row_type == 'hydrogen':
            if is_donor:
                return 'HydrogenDonor'
            else:
                return 'HydrogenAcceptor'
        elif row_type == 'salt':
            if is_donor:
                return 'PositiveIon'
            else:
                return 'NegativeIon'
        elif row_type == 'hydrophobic':
            return 'Hydrophobic'
        else:
            return None

    def analyze_sphere_pairs(self):
        for interaction in self.pharmit_spheres_type_available:
            for pharmit_sphere in self.spheres_dict[interaction]['pharmit_spheres']:
                self._interaction_distance_check(pharmit_sphere, interaction)
        self.check_feature_number()

    def _interaction_distance_check(self, pharmit_sphere: PharmaSphere, interaction: str):
        opposite_interaction = self.spheres_dict[interaction]['opposite']
        if not self.spheres_dict[opposite_interaction]['plip_spheres']:
            return
        for plip_sphere in self.spheres_dict[opposite_interaction]['plip_spheres']:
            plip_index = plip_sphere.index
            distance = pharmit_sphere.distance_to(plip_sphere)
            if distance > self.plip_df['avg_dist'][plip_index]:
                self.spheres_dict[interaction]['pharmit_spheres'].remove(pharmit_sphere)
            else:
                pharmit_sphere.quantity_matched = plip_sphere.quantity

    def check_feature_number(self):
        analyzed_quantities = []
        for key, dicti in self.spheres_dict.items():
            opposite = self.spheres_dict[key]['opposite']
            plip_list = self.spheres_dict[opposite]['plip_spheres']
            if not dicti['pharmit_spheres']:
                continue
            if len(dicti['pharmit_spheres']) > dicti['enabled']:
                if dicti['enabled'] == 0:
                    self._create_interaction_sphere(plip_list, analyzed_quantities, dicti['pharmit_spheres'],
                                                    1)
                else:
                    dicti['pharmit_spheres'].sort(key=lambda x: x.quantity_matched, reverse=True)
                    dicti['pharmit_spheres'] = dicti['pharmit_spheres'][:dicti['enabled']]
            elif dicti['pharmit_spheres'] < dicti['enabled']:
                spheres_to_create = dicti['enabled'] - len(dicti['pharmit_spheres'])
                analyzed_quantities = [pharmit_sphere.quantity_matched for pharmit_sphere in dicti['pharmit_spheres']]
                self._create_interaction_sphere(plip_list, analyzed_quantities, dicti['pharmit_spheres'],
                                                spheres_to_create)
            else:
                continue

    @staticmethod
    def _create_interaction_sphere(plip_spheres: list, analyzed_quantities: list, original_pharmit_spheres: list,
                                   quantity_to_create: int):
        """Creates the sphere in pharmit to interact to the plip sphere"""
        pharmit_sphere = None
        for q in range(quantity_to_create):
            for plip_sphere in plip_spheres:
                if plip_sphere.quantity in analyzed_quantities:
                    continue
                else:
                    pharmit_sphere_interaction = plip_sphere.interaction_type
                    pharmit_sphere = PharmaSphere(plip_sphere.x, plip_sphere.y, plip_sphere.z, 1.0,
                                                  pharmit_sphere_interaction, False)
            if not pharmit_sphere:
                continue

            original_pharmit_spheres.append(pharmit_sphere)

    def get_last_pharmit_spheres(self):
        last_pharmit_spheres = []
        for key, dicti in self.spheres_dict.items():
            last_pharmit_spheres += dicti['pharmit_spheres']

        if len(last_pharmit_spheres) > 6:
            last_pharmit_spheres = last_pharmit_spheres[:6]
        
        return last_pharmit_spheres

    def run_pharma_optimizer(self):
        self._generate_pharmit_spheres()
        self._generate_plip_spheres()
        self.analyze_sphere_pairs()
        return self.get_last_pharmit_spheres()


if __name__ == '__main__':
    pharmit_json_path = '/home/kdunorat/Projetos/LambdaPipe/files/pharmit (3).json'
    plip_csv = '/home/kdunorat/Projetos/LambdaPipe/files/7KR1-pocket3-interact.csv'
    popt = PharmaOptimizer(pharmit_json_path, plip_csv)
    pharmit_spheres_list = popt.run_pharma_optimizer()
    jsh = JsonHandler(output_file_path='/home/kdunorat/Projetos/LambdaPipe/files', pharmit_json=pharmit_json_path)
    jsh.write_points(pharmit_spheres_list)
    jsh.create_json()
