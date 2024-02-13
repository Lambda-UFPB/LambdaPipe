import pandas as pd


class AdmetAnalyzer:
    def __init__(self, csv_path: str, admet_path: str, best_molecules: list):
        self.admet_df = pd.read_csv(csv_path)
        self.admet_path = admet_path
        self.best_molecules = best_molecules

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
        self.admet_df = self.admet_df.reset_index()

    def _get_molecule_id(self):
        mol_ids = []
        for index in self.admet_df['index']:
            mol_ids.append(self.best_molecules[index][0])
        self.admet_df = self.admet_df.drop(columns='index')
        self.admet_df['Molecule ID'] = mol_ids
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

    def run(self):
        self._filter_toxicity()
        self._filter_conditions()
        self._get_molecule_id()
        category_df = self.admet_df.select_dtypes(include=['float64']).map(AdmetAnalyzer._generate_category_df)
        for column in category_df.columns:
            self.admet_df[column] = self.admet_df[column].astype(object)
        self.admet_df.update(category_df)
        self.admet_df.to_csv(f'{self.admet_path}/admet_filtered.csv', index=False)


if __name__ == '__main__':
    lista_final = [('PubChem-140338247', -11.00106, 4.80702, '[H]OC(=C1C=CC=C(C)C1)C(O[H])C(O[H])C(O[H])C(O[H])C(O[H])=C1C=CC=C(C)C1'), ('PubChem-71528416', -11.00147, 4.47418, '[H]OCC1OCCCCN(C(=O)C2=CC=C(F)C=C2)C(CC2=CC=CC=C2)C(=O)N(CC2=CC=C(OC)C=C2)CC(O[H])C(O[H])C1O[H]'), ('PubChem-155566579 PubChem-155566580 CHEMBL4586954 CHEMBL4594798', -11.00254, 4.83762, '[H]OC1=CC=C(CC(C(=O)N([H])C2CSCC3=C(C=CC=C3)CSCC(N([H])C(=O)C(CC3=CC=C(O[H])C=C3)N([H])[H])C(=O)N([H])CC(=O)N([H])C(CC3=CC=C(F)C=C3)C(=O)N([H])N([H])C(=O)C(CC3=CC=C(F)C=C3)N([H])C(=O)CN([H])C2=O)N([H])[H])C=C1'), ('PubChem-91092635', -11.0044, 4.80178, '[H]OC1=C(OC)C(OC2(O[H])C(O[H])(O[H])C(O[H])(O[H])C(O[H])(O[H])C2(O[H])O[H])=C(O[H])C(C2C(O[H])(O[H])C(=O)N([H])C2(O[H])O[H])=C1O[H]'), ('CLPBCJGQNWWKFT-UHFFFAOYSA-N', -11.0048, 2.83903, '[H]OB(O[H])C1=C(N([H])C(=O)C(CC2=CC=C(Cl)C=C2)N([H])S(=O)(=O)C2=CC=CC=C2)C=CC=C1'), ('PubChem-92228856', -11.0065, 4.54798, '[H]OC1=CC=CC2=C1C(O[H])=C1C(=O)C3(O[H])C(O[H])=C(C(=O)N([H])CN([H])C4=NC=C(C(=O)N([H])[H])C=C4)C(=O)C(N(C)C)C3CC1=C2C'), ('PubChem-136376106', -11.01391, 4.36058, '[H]N=C(C1=C(N([H])C(C2=CC(OC)=C(OC)C=C2F)C2=NN(C3=CC=CC=C3N([H])[H])C(=O)N2[H])C=C(OC(=O)C(F)(F)F)C=C1)N([H])[H]'), ('PubChem-91184504', -11.01512, 4.45145, '[H]OC1=C(F)C(O[H])=C(O[H])C(C2CC(N3C(O[H])(O[H])C(O[H])(O[H])N(C(C)=O)C(O[H])(O[H])C3(O[H])O[H])CCN2COCN(C)C(C)C2=C(O[H])C(C(F)(F)F)=C(O[H])C(C(F)(F)F)=C2O[H])=C1C'), ('PubChem-157347337', -11.01595, 6.16929, '[H]OC(=O)C(CCCCN([H])[H])N([H])C(=O)C1CC(=O)C(CC2=CC=CC=C2)N([H])C(=O)C(CC2=CC=C(C3=CC=CC=C3)C=C2)N([H])C(=O)C(CC2=CC=CS2)N([H])C(=O)C(O[H])C(O[H])C(=O)N([H])C2=CC=C(C=C2)C1'), ('PubChem-163592342', -11.01956, 2.55583, '[H]OCC1OC(SC2=CC=CC(OC(F)(F)F)=C2)C(O[H])C(N([H])C=C(C2=CC(F)=C(F)C(F)=C2)N([H])N([H])[H])C1O[H]'), ('CHEMBL502219 PubChem-44560869', -11.02074, 3.36475, '[H]OC(C)C1C(=O)N([H])C(C(=O)N([H])C(CC2=CC=C3C=CC=CC3=C2)C(=O)N([H])[H])CSSCC(N([H])C(=O)C(CC2=CC=C(Cl)C=C2)N([H])[H])C(=O)N([H])C(CC2=CC=C(N([H])C(=O)N([H])[H])C=C2)C(=O)N([H])C(CC2=CN([H])C3=CC=CC=C23)C(=O)N([H])C(CCCCN([H])[H])C(=O)N1[H]'), ('PubChem-11980979 PubChem-11980980', -11.02626, 3.30828, '[H]N1C2=CC=CC=C2N=C1N([H])C1=NC2(C3=CC=CC=C3)N=C(N([H])C3=NC4=CC=CC=C4N3[H])N([H])C2(C2=CC=CC=C2)N1[H]'), ('PubChem-57104119', -11.02732, 5.37823, '[H]N(CCCCCCCC)C1C(F)C(F)C(F)C2C1C1N([H])C2N([H])C2C3CC(F)C(F)C(F)C3C(N2[H])N([H])C2C3C(F)C(F)C(F)C(F)C3C(N([H])C3C4C(F)C(F)C(F)C(F)C4C(N1[H])N3[H])N2F'), ('PubChem-156031028', -11.02866, 1.69068, '[H]OCC1OC(S(=O)C2=CC(Cl)=C(Cl)C=C2)C(O[H])C(N([H])C=C(C2=CC(F)=C(F)C(F)=C2)N([H])N([H])[H])C1O[H]'), ('PubChem-159824761 PubChem-159824762', -11.0305, 6.25564, '[H]OC1CCC(O[H])C(O[H])CC(O[H])CC2(O[H])CC(O[H])C(N([H])C(=O)N([H])CCC(C)=O)C(CC(OC3OC(C)C(C)C(N([H])[H])C3O[H])C=CC=CC=CC=CC=CC=CC=CC(C)C(O[H])C(C)C(C)OC(=O)CC(O[H])C1)O2'), ('CHEMBL1075971', -11.03685, 4.01435, '[H]OC1=C2C(=O)C3=C(O[H])C(C4=CC=C5OC6(C(=O)OC)C(=C(O[H])CC(C)C6O[H])C(O[H])C5=C4O[H])=CC=C3OC2(C(=O)OC)C(O[H])C(C)C1'), ('PubChem-44460577 CHEMBL80024', -11.03697, 5.74672, '[H]OC1=CC2=C(C(O[H])=C1O[H])C1=C(O[H])C(O[H])=C3OC(=O)C4=C5C(=C(O[H])C(O[H])=C4C4=C(C=C(O[H])C(O[H])=C4O[H])C(=O)OC4C(CC2=O)OC(O[H])C(O[H])C4O[H])OC(=O)C1=C35'), ('PubChem-89989988', -11.04241, 5.33368, '[H]N1C2=CC=CC=C2C(C(C2=CC=CC=C2)C2=C(C(=O)N([H])N([H])C(=O)N([H])N([H])C)N([H])C3=CC=CC=C32)=C1C(=O)N([H])N([H])C'), ('PubChem-163533774', -11.04337, 3.96125, '[H]N([H])C(C)=C1C(=C(C)N([H])N([H])C(C2=C(C)C(N([H])[H])=C(N([H])[H])C(N([H])CC(=C(C(=C(C)N([H])[H])N([H])[H])N([H])[H])N([H])[H])=C2N([H])[H])=C(C)N([H])[H])C(N([H])[H])=C(N([H])[H])C(N([H])[H])=C1N([H])[H]'), ('ZINC000952856870 952856870 MCULE-9659922755 MolPort-045-918-439 PubChem-131923668', -11.04407, 2.58335, '[H]OC(C)C1C(=O)N([H])C(C(C)O[H])C(=O)N([H])C(CC2=CC=CC=C2)C(=O)N([H])CC2=CN(CCCOC3=C(C=CC(Cl)=C3)C(=O)N1[H])N=N2'), ('PubChem-102240413', -11.04844, 3.10522, '[H]OCC(O[H])C(O[H])C(O[H])C1OC2=C(C(O[H])=C(C(=O)C=CC3=CC=C(O[H])C=C3)C(=O)C2(O[H])C2OC(CO[H])C(O[H])C(O[H])C2O[H])C1C1=C(O[H])C(=C(C=CC2=CC=C(O[H])C=C2)O[H])C(=O)C(O[H])(C2OC(CO[H])C(O[H])C(O[H])C2O[H])C1=O'), ('CHEMBL197165 PubChem-5327090', -11.04981, 3.94963, '[H]OC1CC2=CC=CC=C2C1N([H])C(=O)C(CC1=CC=CC=C1)(CN(CC1=CC=CC=C1)N([H])C(=O)C(C(C)C)N([H])C(=O)OC)O[H]'), ('MolPort-023-277-075 PubChem-90488914', -11.05441, 2.83991, '[H]OCC1OC(OC2C(O[H])C(N([H])[H])CC(N([H])C)C2O[H])C2OC3(OC2C1O[H])OC(C(CO[H])N([H])[H])C(O[H])C(O[H])C3O[H]'), ('PubChem-155124754', -11.05523, 4.23382, '[H]N1C(=O)C(N([H])C(=O)N([H])N([H])C(=O)C2=C(C3=CN=C(C4CC4)N=C3)C=C(C)C=N2)N=C(C2=CC=CC=C2)C2=CC=CC=C21'), ('ZINC000252459988 252459988', -11.05665, 6.44992, '[H]N=C(N([H])[H])N([H])C1C(O[H])C(O[H])C(OC2OC(C)C(CO[H])(O[H])C2OC2OC(CO[H])C(O[H])C(O[H])C2N([H])C)C(N([H])C(=N[H])N([H])[H])C1O[H]'), ('PubChem-131954263', -11.06003, 2.15394, '[H]N1CCC2C(C1=O)C(N([H])C1=CC=CC(C)=C1)N([H])C(N([H])C1CCCCC1N([H])[H])N2[H]'), ('PubChem-57712602', -11.06169, 4.30835, '[H]OC1CC2C(=O)N([H])C(CC3=CC=CC=C3)C(=O)N([H])C(CCCN=C(N([H])[H])N([H])[H])C(O[H])N([H])C(CC3=CN([H])C4=CC=CC=C34)C(O[H])N([H])C(C(O[H])N([H])[H])CCCCN([H])C(=O)CCC(C)C(=O)N2C1'), ('PubChem-90854313', -11.06344, 4.51265, '[H]OC1=C(O[H])C(O[H])=C(C(O[H])(O[H])N2C(O[H])(O[H])C(O[H])(O[H])C(O[H])(C(O[H])(O[H])C3(O[H])C(=O)C4=C(C(O[H])=C(OC)C(OC)=C4O[H])C3(O[H])O[H])C(O[H])(O[H])C2(O[H])O[H])C(O[H])=C1O[H]'), ('PubChem-90962782', -11.06698, 4.43933, '[H]N([H])CCCC(CC(=O)N([H])C1CN([H])C(=O)C(C2CCN=C(N([H])[H])N2[H])N([H])C(=O)C(=CN([H])C(=O)N([H])[H])N([H])C(=O)C(CN([H])[H])N([H])C(=O)C(C)N([H])C1=O)N([H])[H]'), ('PubChem-76182357', -11.06889, 4.83405, '[H]OC1=C2C(=O)C3(O[H])C(O[H])=C(C(=O)N([H])[H])C(=O)C(N(C)C)C3C(O[H])C2C(C)C2=C1C(O[H])=C(N([H])C(=O)N([H])C1=CC=CC=C1)C=C2'), ('ZINC000015974021 ZINC15974021 15974021 MolPort-000-701-367 PubChem-135403374 PubChem-135517085', -11.06956, 3.51588, '[H]N(CC1=CC=CC=C1)C(=S)N([H])N([H])C1=NC2=C(C(=O)N1[H])C1(CCCCC1)CC1=CC=CC=C12'), ('ZINC000952856254 952856254 MCULE-5736259561 MolPort-045-916-987 PubChem-131931924', -11.07391, 0.90856, '[H]OC(C)C1C(=O)N([H])C(C(C)O[H])C(=O)N([H])C(CC2=CC=CC=C2)C(=O)N([H])CC2=CN(CCCOC3=C(C=CC(Cl)=C3)C(=O)N1[H])N=N2'), ('ZINC001772702421 1772702421', -11.08279, 2.69319, '[H]OC(C)C1C(=O)N([H])C(C)C(=O)N([H])C(CC2=CC=CC=C2)C(=O)N([H])CCOC2=CC=C(C=C2)OC2(CCN(C(=O)C3=CC=CC=C3C3=NC=CN3C)CC2)C(=O)N1[H]'), ('MolPort-001-789-147 MCULE-2875253547', -11.08392, 6.12162, '[H]OC1=C(N=NC2=C([As](=O)(O[H])O[H])C=CC=C2)C(S(=O)(=O)O[H])=CC2=CC(S(=O)(=O)O[H])=C(N=NC3=C([As](=O)(O[H])O[H])C=CC=C3)C(O[H])=C21'), ('CHEMBL1950444 PubChem-57334109', -11.09167, 6.07675, '[H]N1C2=CC(Cl)=C(Cl)C=C2N=C1C(C)N([H])C(=O)C(C(C)C1=CC=C(C2=CC=CC=C2)C=C1)N([H])C(=O)C(C)(C)N([H])[H]'), ('PubChem-137475358', -11.09178, 4.67096, '[H]OC1=CC=CC2=C1C(O[H])=C1C(=O)C3(O[H])C(O[H])=C(C(=O)N([H])[H])C(=O)C(N(C)C)C3C(OCC3=CC=CC=C3)C1C2=C'), ('PubChem-21714146', -11.09313, 3.31255, '[H]N1C(C(=O)N([H])N([H])C(=O)C(CC2=CC=CC=C2)N([H])C(=O)COC2=CC=CC=C2)=CC2=CC=CC=C21'), ('PubChem-134297653', -11.09329, 4.46457, '[H]ON([H])C1=NC(N([H])C(=O)N([H])C2=CC3=C(C=CC(CN(C)CCCN([H])C4C(C5CCCCCC5)C(C(C)C)N([H])C(N([H])C(=O)N([H])C5=CC6=CC=CC=C6C=C5)N4[H])=C3)C=C2)=NC(C(C)C)=C1'), ('PubChem-90967224', -11.09665, 5.26153, '[H]OC1=C(F)C(O[H])=C(O[H])C(C2N(C(=O)N(C)C(C)C3=C(O[H])C(C(F)(F)F)=C(O[H])C(C(F)(F)F)=C3O[H])C(O[H])(O[H])C(O[H])(O[H])C(N3CCN(C(C)=O)CC3)C2(O[H])O[H])=C1C'), ('CHEMBL191998', -11.10753, 4.70547, '[H]N=C(N([H])[H])N([H])CCC(=O)N([H])C1CC=CCC(C(=O)N([H])CCC2=CC=C(O[H])C=C2)N([H])C(=O)C(CC2=CC3=C(C=CC=C3)C=C2)N([H])C(=O)C(CCCN=C(N([H])[H])N([H])[H])N([H])C1=O'), ('ZINC001570003472 1570003472', -11.10855, 6.04798, '[H]OCC1OC(OCC2OC(OC3=C(C4=CC=C(O[H])C(O[H])=C4)OC4=CC(O[H])=CC(O[H])=C4C3=O)C(O[H])C(O[H])C2O[H])CC(O[H])C1O[H]'), ('PubChem-156886368 PubChem-156886369', -11.10881, 4.53982, '[H]OC1=CC=CC=C1C1=CC(OCCC2=CC=C(CN([H])[H])C=C2)=C(N([H])[H])N([H])N1[H]'), ('CHEMBL3984228 PubChem-134157101', -11.1091, 3.1123, '[H]OC1=CC=C(N([H])C(=O)N([H])N([H])C(=O)C2C(=O)N([H])C(=O)N(C3=CC=CC=C3)C2=O)C=C1'), ('PubChem-163148662', -11.11294, 4.47703, '[H]OC(C)C(CC1=C2C3C(C=CC(C4=CN([H])C(N([H])[H])C=C4)CC34CC(O[H])C(O[H])CC4C1=O)CC1(C)C(C(C)(O[H])C(O[H])C3OC4CCC(CCC)CCC4C3C)CCC21O[H])O[H]'), ('ZINC000056897567 56897567 PubChem-94658548', -11.11356, 4.39698, '[H]OCC(O[H])C(O[H])C(O[H])C(O[H])C(OC1OC(CO[H])C(O[H])C(N([H])[H])C1O[H])C1OC(N2C=CC(N([H])[H])=NC2=O)C(O[H])C(O[H])C1N([H])[H]'), ('PubChem-156464063', -11.11758, 3.38122, '[H]OC1=CC=C(C(O[H])C(O[H])C2C(=O)N([H])C(C(C)O[H])C(=O)N3CC(C)C(O[H])C3C(=O)N([H])C(OCC3CC[N+]3(C)C)C(O[H])CC(N([H])C(=O)C3=CC=C(C4=CC=C(C5=CC=C(OCCCCC)C=C5)C=C4)C=C3)C(=O)N([H])C(C(C)O[H])C(=O)N3CC(O[H])CC3C(=O)N2[H])C=C1'), ('PubChem-129181867', -11.11847, 5.64509, '[H]OCC1=CC2C(=O)C3(C=C(C)C(N(C=C(CC4=CC=CC=C4)N([H])[H])N([H])[H])C3(O[H])C1O[H])CCC(C)C2(C)C'), ('CHEMBL2448140 PubChem-15593120', -11.12035, 5.90077, '[H]OC1=CC2=C(CC(OC(=O)C3=CC(O[H])=C(O[H])C(O[H])=C3)C(C3=CC(O[H])=C(O[H])C(O[H])=C3C3=C(O[H])C(O[H])=C(O[H])C=C3C3OC4=C(CC3OC(=O)C3=CC(O[H])=C(O[H])C(O[H])=C3)C(O[H])=CC(O[H])=C4)O2)C(O[H])=C1'), ('MolPort-045-933-364 MCULE-9233237773 PubChem-131925749 ZINC000952862824', -11.12207, 4.37113, '[H]OC(=O)C1CSC2=C(CC(N([H])C(=O)C3=CN(C(C)C)N=C3)C(=O)N([H])C(CC(C)C)C(=O)N([H])C(C)C(=O)N([H])C(C(C)O[H])C(=O)N1[H])C1=CC=CC=C1N2[H]'), ('CHEMBL552154', -11.12313, 5.42986, '[H]N=C(N([H])[H])N([H])CCCC1C(=O)N([H])C(CC2=CN([H])C3=CC=CC=C23)C(=O)N([H])C(C(=O)N([H])[H])CSC2=CC=C([N+](=O)[O-])C=C2C(=O)N2CC(O[H])CC2C(=O)N([H])C(CC2=CC=CC=C2)C(=O)N1[H]')]
    aa = AdmetAnalyzer('/home/kdunorat/PycharmProjects/LambdaPipe/admet/merged.csv',
                       '/home/kdunorat/PycharmProjects/LambdaPipe/admet', lista_final)
    aa.run()