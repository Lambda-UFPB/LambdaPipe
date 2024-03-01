import json
import pandas as pd
from pharma_sphere import PharmaSphere


class PharmaOptimizer:
    def __init__(self, pharmit_session: str, plip_csv_path: str):
        self.plip_df = pd.read_csv(plip_csv_path)
        self.mean_quantity = self.plip_df['quantidade'].mean()
        self.pharmit_session = pharmit_session
        self.interaction_dict = {
            'Hydrophobic': [0, 'hydrophobic'],
            'HydrogenDonor': [0, 'hydrogen'],
            'HydrogenAcceptor': [0, 'hydrogen'],
            'PositiveIon': [0, 'salt'],
            'NegativeIon': [0, 'salt']
        }
        self.spheres_dict = {
            'hydrophobic': [],
            'hydrogen': [[], [], []],
            'salt': [[], [], []],
        }

    def generate_pharmit_spheres(self):

        with open(self.pharmit_session, 'r') as file:
            session = json.load(file)
        pharmit_spheres_type_available = []
        for feature in session['points']:
            if feature['name'] == 'InclusionSphere' or feature['name'] == 'Aromatic':
                continue
            if feature['enabled']:
                self.interaction_dict[feature['name']][0] += 1

            if 'Donor' in feature['name'] or 'Positive' in feature['name']:
                is_donor = True
            else:
                is_donor = False
            if self.interaction_dict[feature['name']][1] not in pharmit_spheres_type_available:
                pharmit_spheres_type_available.append(self.interaction_dict[feature['name']][1])

            self.spheres_dict[self.interaction_dict[feature['name']][1]][0].append(PharmaSphere(feature['x'],
                                                                                                feature['y'],
                                                                                                feature['z'],
                                                                                                feature['radius'],
                                                                                                feature['name'],
                                                                                                is_donor))

        return pharmit_spheres_type_available

    def generate_plip_spheres(self, pharmit_spheres_type_available: list):
        for index, row in self.plip_df.iterrows():
            if row['type'] in pharmit_spheres_type_available and row['quantidade'] >= 300:
                if pd.isna(row['protis']):
                    is_donor = None
                else:
                    is_donor = row['protis']
                self.spheres_dict[row['type']][1].append((PharmaSphere(row['x'], row['y'], row['z'], row['raio'],
                                                                       row['type'], is_donor=is_donor), index))

    def analyze_sphere_pairs(self):
        analyzed_plip_spheres_count = 0
        for interaction in self.spheres_dict.keys():
            for plip_tuple in self.spheres_dict[interaction][1]:
                plip_sphere, plip_index = plip_tuple
                for index_pharmit, pharmit_sphere in enumerate(self.spheres_dict[interaction][0]):
                    if self.calculate_interaction(pharmit_sphere, plip_sphere, plip_index, interaction):
                        analyzed_plip_spheres_count += 1
            self.check_feature_number(interaction, analyzed_plip_spheres_count)

    def calculate_interaction(self, pharmit_sphere: PharmaSphere, plip_sphere: PharmaSphere,
                              plip_index: int, interaction: str):
        plip_interaction_quantity = self.plip_df['quantidade'][plip_index]
        distance = pharmit_sphere.distance_to(plip_sphere)
        if distance <= self.plip_df['avg_dist'][plip_index] and plip_interaction_quantity > self.mean_quantity:
            if interaction == 'hydrophobic':
                self.spheres_dict[interaction][2].append((pharmit_sphere, distance))
                return True
            else:
                if pharmit_sphere.is_donor != plip_sphere.is_donor:
                    self.spheres_dict[interaction][2].append((pharmit_sphere, distance))
                    return True
        else:
            return False

    def check_feature_number(self, interaction: str, analyzed_plip_spheres_count: int):
        already_enabled_append = False
        already_disabled_append = False
        keys_from_interact = [key for key, value in self.interaction_dict.items() if interaction in value]
        for key in keys_from_interact:
            if len(self.spheres_dict[interaction][2]) < self.interaction_dict[key][0]:
                spheres_to_create = self.interaction_dict[key][0] - len(self.spheres_dict[interaction][2])
                plip_spheres_remaining = self.spheres_dict[interaction][1][analyzed_plip_spheres_count:]

                for index, plip_sphere in plip_spheres_remaining:
                    if index >= spheres_to_create:
                        break
                    pharmit_sphere = self.create_interaction_sphere(plip_sphere)
                    self.spheres_dict[interaction][2].append((pharmit_sphere, 0))

            elif len(self.spheres_dict[interaction][2]) > self.interaction_dict[key][0]:
                self.spheres_dict[interaction][2].sort(key=lambda x: x[1])
                if self.interaction_dict[key][0] == 0:
                    for index_tuple, spheres_tuple in enumerate(self.spheres_dict[interaction][2]):
                        spheres_name = spheres_tuple[0].interaction_type
                        if key == spheres_name:
                            self.spheres_dict[interaction][2] = [self.spheres_dict[interaction][2][index_tuple]]
                            break
                        self.spheres_dict[interaction][2] = [self.spheres_dict[interaction][2][0]]

                else:
                    if not already_enabled_append:

                        self.spheres_dict[interaction][2] = self.spheres_dict[interaction][2][:self.interaction_dict[key][0]]
                        self.spheres_dict[interaction][2].append
                    already_enabled_appended = True
    @staticmethod
    def create_interaction_sphere(plip_sphere: PharmaSphere):
        """Creates the sphere in pharmit to interact to the plip sphere"""
        if plip_sphere.interaction_type == 'hydrogen':
            if plip_sphere.is_donor:  # if protein is donor
                pharmit_sphere_interaction = 'HydrogenAcceptor'
            else:
                pharmit_sphere_interaction = 'HydrogenDonor'
        elif plip_sphere.interaction_type == 'salt':
            if plip_sphere.is_donor:
                pharmit_sphere_interaction = 'NegativeIon'
            else:
                pharmit_sphere_interaction = 'PositiveIon'
        else:
            pharmit_sphere_interaction = 'Hydrophobic'

        pharmit_sphere = PharmaSphere(plip_sphere.x, plip_sphere.y, plip_sphere.z, 1.0,
                                      pharmit_sphere_interaction, False)

        return pharmit_sphere

    def get_last_pharmit_spheres(self):
        last_pharmit_spheres = []
        #print(self.spheres_dict['hydrophobic'][2])
        #print(len(self.spheres_dict['hydrogen'][2]))
        for triple_list in self.spheres_dict.values():
            for sphere_tuple in triple_list[2]:
                last_pharmit_spheres.append(sphere_tuple[0])

        if len(last_pharmit_spheres) > 6:
            last_pharmit_spheres = last_pharmit_spheres[:5]
        
        return last_pharmit_spheres

    def run_pharma_optimizer(self):
        pharmit_spheres_type_available = self.generate_pharmit_spheres()
        self.generate_plip_spheres(pharmit_spheres_type_available)
        print(len(self.spheres_dict['hydrogen'][2]))
        self.analyze_sphere_pairs()
        print(len(self.spheres_dict['hydrogen'][2]))
        return self.get_last_pharmit_spheres()


if __name__ == '__main__':
    pharmit_json_path = '/home/kdunorat/Projetos/LambdaPipe/files/pharmit (3).json'
    plip_csv = '/home/kdunorat/Projetos/LambdaPipe/files/7KR1-pocket3-interact.csv'
    popt = PharmaOptimizer(pharmit_json_path, plip_csv)
    pharmit_spheres_list = popt.run_pharma_optimizer()
    #print(pharmit_spheres_list)
