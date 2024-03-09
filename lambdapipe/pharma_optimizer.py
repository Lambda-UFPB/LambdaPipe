import json
import pandas as pd
from pharma_sphere import PharmaSphere


class PharmaOptimizer:
    def __init__(self, pharmit_session: json, plip_csv_path: str):
        self.pharmit_session = pharmit_session
        self.plip_df = pd.read_csv(plip_csv_path)
        self.mean_quantity = self.plip_df['quantidade'].mean()
        self.spheres_dict = {
            'Hydrophobic': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'Hydrophobic',
                            'pharmit_final_size': 0},
            'HydrogenDonor': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenAcceptor',
                              'pharmit_final_size': 0},
            'HydrogenAcceptor': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenDonor',
                                 'pharmit_final_size': 0},
            'PositiveIon': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'NegativeIon',
                            'pharmit_final_size': 0},
            'NegativeIon': {'enabled': 0, 'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'PositiveIon',
                            'pharmit_final_size': 0}
        }
        self.pharmit_spheres_type_available = []

    def _generate_pharmit_spheres(self):
        pharmit_spheres_type_available = []
        for feature in self.pharmit_session['points']:
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
            if row['quantidade'] > self.mean_quantity:
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
        self._get_new_pharmit_spheres_list()

    def _interaction_distance_check(self, pharmit_sphere: PharmaSphere, interaction: str):
        opposite_interaction = self.spheres_dict[interaction]['opposite']
        if not self.spheres_dict[opposite_interaction]['plip_spheres']:
            return
        match = False
        for plip_sphere in self.spheres_dict[opposite_interaction]['plip_spheres']:
            plip_index = plip_sphere.index
            distance = pharmit_sphere.distance_to(plip_sphere)
            if distance < self.plip_df['avg_dist'][plip_index]:
                if plip_sphere.quantity > pharmit_sphere.quantity_matched:
                    pharmit_sphere.quantity_matched = plip_sphere.quantity
                    pharmit_sphere.distance = distance
                match = True
        if not match:
            self.spheres_dict[interaction]['pharmit_spheres'].remove(pharmit_sphere)

    def _get_new_pharmit_spheres_list(self):
        for key, dicti in self.spheres_dict.items():
            opposite = self.spheres_dict[key]['opposite']
            plip_opp_list = self.spheres_dict[opposite]['plip_spheres']
            if not dicti['pharmit_spheres']:
                continue
            if dicti['enabled'] > 0:
                if len(dicti['pharmit_spheres']) < dicti['enabled']:
                    quantity_to_create = dicti['enabled'] - len(dicti['pharmit_spheres'])
                    quantity_analyzed = [x.quantity_matched for x in dicti['pharmit_spheres']]
                    final_spheres = self._create_interaction_sphere(plip_opp_list, quantity_to_create,
                                                                    quantity_analyzed, key)
                    dicti['pharmit_spheres'] += final_spheres
                elif len(dicti['pharmit_spheres']) > dicti['enabled']:
                    dicti['pharmit_spheres'].sort(key=lambda x: x.quantity_matched, reverse=True)
                    dicti['pharmit_spheres'] = dicti['pharmit_spheres'][:dicti['enabled']]
            if dicti['enabled'] == 0:
                dicti['pharmit_spheres'].sort(key=lambda x: x.quantity_matched, reverse=True)
                dicti['pharmit_spheres'] = [dicti['pharmit_spheres'][0]]

    @staticmethod
    def _create_interaction_sphere(plip_spheres: list, quantity_to_create: int, quantity_analyzed: list,
                                   interaction: str):
        """Creates the sphere in pharmit to interact to the plip sphere"""
        new_spheres = []
        new_plip_spheres = []
        plip_spheres.sort(key=lambda x: x.quantity, reverse=True)
        for sphere in plip_spheres:
            if sphere.quantity not in quantity_analyzed:
                new_plip_spheres.append(sphere)
        used_plip_spheres = []
        for q in range(quantity_to_create):
            plip_sphere = new_plip_spheres[q]
            if plip_sphere in used_plip_spheres:
                continue
            pharmit_sphere = PharmaSphere(plip_sphere.x, plip_sphere.y, plip_sphere.z, 1.0, interaction, False)
            pharmit_sphere.quantity_matched = plip_sphere.quantity
            new_spheres.append(pharmit_sphere)
            used_plip_spheres.append(plip_sphere)
        return new_spheres

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
