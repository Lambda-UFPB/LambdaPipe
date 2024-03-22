import json
import pandas as pd
from pharma_sphere import PharmaSphere


class PharmaOptimizer:
    def __init__(self, pharmit_session: json, plip_csv_path: str):
        self.pharmit_session = pharmit_session
        self.plip_df = pd.read_csv(plip_csv_path)
        self.mean_quantity = self.plip_df['quantidade'].mean()
        self.spheres_dict = {
            'Hydrophobic': {'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'Hydrophobic',
                            'pharmit_final_size': 0},
            'HydrogenDonor': {'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenAcceptor',
                              'pharmit_final_size': 0},
            'HydrogenAcceptor': {'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'HydrogenDonor',
                                 'pharmit_final_size': 0},
            'PositiveIon': {'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'NegativeIon',
                            'pharmit_final_size': 0},
            'NegativeIon': {'pharmit_spheres': [], 'plip_spheres': [], 'opposite': 'PositiveIon',
                            'pharmit_final_size': 0}
        }
        self.pharmit_spheres_type_available = []
        self.spheres_in_interaction_limit = 0
        self.total_pharmit_spheres = 0

    def _generate_pharmit_spheres(self):
        pharmit_spheres_type_available = []
        for feature in self.pharmit_session['points']:
            if feature['name'] == 'InclusionSphere' or feature['name'] == 'Aromatic':
                continue

            is_donor = self._check_donor(pharmit_feature=feature)

            if feature['name'] not in pharmit_spheres_type_available:
                self.pharmit_spheres_type_available.append(feature['name'])

            self.spheres_dict[feature['name']]['pharmit_spheres'].append(PharmaSphere(feature['x'], feature['y'],
                                                                                      feature['z'], feature['radius'],
                                                                                      feature['name'], is_donor))
            self.total_pharmit_spheres += 1

    def _generate_plip_spheres(self):
        for index, row in self.plip_df.iterrows():
            is_donor = self._check_donor(plip_row=row)
            plip_interaction_type = self._plip_new_interaction_type(row['type'], is_donor)
            if plip_interaction_type in self.pharmit_spheres_type_available:
                plip_sphere = PharmaSphere(row['x'], row['y'], row['z'], row['raio'], plip_interaction_type,
                                           is_donor, index=index)
                plip_sphere.quantity = row['quantidade']
                self.spheres_dict[plip_interaction_type]['plip_spheres'].append(plip_sphere)

    def _get_pharmacophore_limit(self):
        plip_sphere_size = []
        for dicti in self.spheres_dict.values():
            if len(dicti['plip_spheres']) == 0:
                continue
            plip_sphere_size.append(len(dicti['plip_spheres']))
        self.spheres_in_interaction_limit = min(plip_sphere_size)

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

    def _analyze_sphere_pairs(self):
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
        print(self.total_pharmit_spheres)
        new_total_pharmit_spheres = sum(len(value['pharmit_spheres']) for value in self.spheres_dict.values())
        analyzed_interactions = [(x.quantity_matched, x.interaction_type) for x in self._get_last_pharmit_spheres()]
        print(new_total_pharmit_spheres)
        all_plip_spheres = []
        if new_total_pharmit_spheres < 5:
            quantity_to_create = 5 - new_total_pharmit_spheres
            for value in self.spheres_dict.values():
                all_plip_spheres.extend(value['plip_spheres'])
            ranked_plip_spheres = sorted(all_plip_spheres, key=lambda sphere: sphere.quantity, reverse=True)
            for index, plip_sphere in enumerate(ranked_plip_spheres):
                interaction = (plip_sphere.quantity, plip_sphere.interaction_type)
                if index == quantity_to_create:
                    break
                if interaction in analyzed_interactions:
                    continue
                if plip_sphere.interaction_type == 'Hydrophobic':
                    continue
                opposite = self.spheres_dict[plip_sphere.interaction_type]['opposite']
                new_sphere = self._create_interaction_sphere(plip_sphere.x, plip_sphere.y, plip_sphere.z,
                                                             opposite, plip_sphere.quantity, plip_sphere.is_donor)
                self.spheres_dict[opposite]['pharmit_spheres'].append(new_sphere)

    @staticmethod
    def _create_interaction_sphere(x, y, z, interaction, quantity, is_donor):
        """Creates the sphere in pharmit to interact to the plip sphere"""
        is_donor = not is_donor
        new_pharmit_sphere = PharmaSphere(x, y, z, 1.0, interaction, is_donor=is_donor)
        new_pharmit_sphere.quantity_matched = quantity
        return new_pharmit_sphere

    def _factor_multiplier(self, factor, decrease=False):
        if decrease:
            for pharmit_sphere in self.spheres_dict['Hydrophobic']['pharmit_spheres']:
                pharmit_sphere.quantity_matched *= factor
        else:
            for key in ['HydrogenDonor', 'HydrogenAcceptor', 'PositiveIon', 'NegativeIon']:
                for pharmit_sphere in self.spheres_dict[key]['pharmit_spheres']:
                    pharmit_sphere.quantity_matched *= factor

    def _get_last_pharmit_spheres(self):
        last_pharmit_spheres = []
        for key, dicti in self.spheres_dict.items():
            last_pharmit_spheres += dicti['pharmit_spheres']

        return last_pharmit_spheres

    def run_pharma_optimizer(self):
        self._generate_pharmit_spheres()
        self._generate_plip_spheres()
        self._get_pharmacophore_limit()
        self._analyze_sphere_pairs()
        self._factor_multiplier(1.5)
        self._factor_multiplier(0.2, decrease=True)
        return self._get_last_pharmit_spheres()
