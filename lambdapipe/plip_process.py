import json
import pandas as pd
from pharma_sphere import PharmaSphere


def generate_pharmit_spheres():
    interaction_enabled_dict = {
        'Hydrophobic': (0, 5),
        'HydrogenDonor': (0, 3.5),
        'HydrogenAcceptor': (0, 3.5),
        'PositiveIon': (0, 3.5),
        'NegativeIon': (0, 3.5),
    }
    with open('/home/kdunorat/Projetos/LambdaPipe/files/pharmit (3).json', 'r') as file:
        session = json.load(file)
    pharmit_spheres_list = []
    for feature in session['points']:
        if feature['name'] == 'InclusionSphere' or feature['name'] == 'Aromatic':
            continue
        if feature['enabled']:
            interaction_enabled_dict[feature['name']] += 1

        pharmit_spheres_list.append(PharmaSphere(feature['x'], feature['y'], feature['z'], feature['radius'],
                                                 feature['name']))

    return pharmit_spheres_list, interaction_enabled_dict


def generate_plip_spheres():
    plip_df = pd.read_csv('/home/kdunorat/Projetos/LambdaPipe/files/7KR1-pocket3-interact.csv')
    plip_spheres_list = []
    for index, row in plip_df.iterrows():
        plip_spheres_list.append(PharmaSphere(row['x'], row['y'], row['z'], row['radius'], row['interaction_type']))


if __name__ == '__main__':
    lista, enabled_dict = generate_pharmit_spheres()
    print(enabled_dict)
