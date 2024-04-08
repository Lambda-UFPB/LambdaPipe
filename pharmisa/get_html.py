import pandas as pd
from ast import literal_eval
from sklearn.preprocessing import MinMaxScaler


def define_globals(df):
    global no_color_columns, normal_values_columns, medicinal_rules_columns, columns_to_clean, strange_columns
    all_columns = df.columns.tolist()
    no_color_columns = ['Molecule ID', 'SMILES', 'Score Pharmit', 'RMSD Pharmit', 'Alarm_NMR', 'BMS', 'Chelating',
                        'PAINS', 'Natural Product-likeness', 't0.5', 'CYP1A2-inh', 'CYP1A2-sub', 'CYP2C19-inh',
                        'CYP2C19-sub', 'CYP2C9-inh', 'CYP2C9-sub', 'CYP2D6-inh', 'CYP2D6-sub', 'CYP3A4-inh',
                        'CYP3A4-sub', 'CYP2B6-inh', 'CYP2B6-sub', 'CYP2C8-inh', 'IGC50', 'LC50DM', 'LC50FM', 'BCF',
                        'NonBiodegradable', 'NonGenotoxic_Carcinogenicity', 'SureChEMBL', 'Skin_Sensitization',
                        'Acute_Aquatic_Toxicity', 'Toxicophores', 'Genotoxic_Carcinogenicity_Mutagenicity']
    columns_to_clean = ['Alarm_NMR', 'BMS', 'PAINS', 'Chelating', 'NonBiodegradable', 'NonGenotoxic_Carcinogenicity',
                        'SureChEMBL', 'Skin_Sensitization', 'Acute_Aquatic_Toxicity', 'Toxicophores',
                        'Genotoxic_Carcinogenicity_Mutagenicity']
    strange_columns = ['QED', 'Fsp3', 'MCE-18', 'caco2', 'cl-plasma']
    normal_values_columns = all_columns[15:21]
    normal_values_columns.extend(all_columns[22:30])
    normal_values_columns.extend(all_columns[66:86])
    normal_values_columns.extend(all_columns[86:98])
    normal_values_columns.extend(['Pharmisa Score', 'toxicity_score', 'medicinal_score', 'absortion_score',
                                  'distribution_score', 'metabolism_score', 'excretion_score', 'tox21_score'])
    medicinal_rules_columns = all_columns[11:15]
    medicinal_rules_columns.extend(['gasa', 'SA-score'])



# Defining the globals
minmax_scaler = MinMaxScaler()
df_old = pd.DataFrame()
no_color_columns, normal_values_columns, medicinal_rules_columns, columns_to_clean, strange_columns = [], [], [], [], []


def color_format(column):
    """Color formatting for the DataFrame."""
    global no_color_columns, normal_values_columns, medicinal_rules_columns, strange_columns
    column_name = column.name
    color = None
    if column_name in no_color_columns:
        return ['background-color: default' for _ in column]
    elif column_name in normal_values_columns:
        color = column.apply(
            lambda val: '#58D68D' if 0 <= float(val) <= 0.3 else ('#F4D03F' if 0.3 < float(val) <= 0.7 else '#EC7063'))
    elif column_name in medicinal_rules_columns:
        color = column.apply(lambda val: '#58D68D' if val in ['Accepted', 'Easy'] else '#EC7063')
    elif column_name in strange_columns:
        if column_name == 'QED':
            color = column.apply(lambda val: '#58D68D' if float(val) > 0.67 else '#EC7063')
        if column_name == 'Fsp3':
            color = column.apply(lambda val: '#58D68D' if float(val) >= 0.42 else '#EC7063')
        if column_name == 'MCE-18':
            color = column.apply(lambda val: '#58D68D' if float(val) >= 45 else '#EC7063')
        if column_name == 'caco2':
            color = column.apply(lambda val: '#58D68D' if float(val) > -5.15 else '#EC7063')
        if column_name == 'cl-plasma':
            color = column.apply(lambda val: '#58D68D' if 0 < float(val) <= 5 else ('#F4D03F' if 5 < float(val) <= 15 else '#EC7063'))
    else:
        return ['background-color: default' for _ in column]

    color = color.apply(lambda val: f'background-color: {val}' if isinstance(val, str) else 'background-color: default')
    return color


def get_df_html(df_html_old: pd.DataFrame):
    """Get the DataFrame with the desired columns and format."""
    global columns_to_clean
    global medicinal_rules_columns
    for column in medicinal_rules_columns:
        if column == 'gasa':
            df_html_old[column] = df_html_old[column].apply(clean_medicinal_columns, rules=False, sascore=False)
        elif column == 'SA-score':
            df_html_old[column] = df_html_old[column].apply(clean_medicinal_columns, rules=False, sascore=True)
        else:
            df_html_old[column] = df_html_old[column].apply(clean_medicinal_columns)
    for column in columns_to_clean:
        df_html_old[column] = df_html_old[column].apply(clean_lists_columns)
    df_html = get_toxicity_score(df_html_old)
    df_html = get_medicinal_score(df_html)
    df_html = get_absortion_score(df_html)
    df_html = get_distribution_score(df_html)
    df_html = get_metabolism_score(df_html)
    df_html = get_excretion_score(df_html)
    df_html = get_tox21_score(df_html)
    df_html = get_pharmisa_score(df_html)
    df_html = df_html.sort_values(by='Pharmisa Score', ascending=True)
    df_html = df_html.reset_index(drop=True)
    first_columns = ['Molecule ID', 'Pharmisa Score', 'toxicity_score', 'medicinal_score',
                     'absortion_score', 'distribution_score', 'metabolism_score', 'excretion_score', 'tox21_score']
    rest_of_columns = [col for col in df_html.columns if col not in first_columns]
    df_html = df_html[first_columns + rest_of_columns]
    df_html['smiles-res'] = df_html['SMILES']
    df_html = df_html.drop(columns=['SMILES'], axis=1)
    df_html['SMILES'] = df_html['smiles-res']
    df_html = df_html.drop(columns=['smiles-res'], axis=1)
    if len(df_html) > 500:
        df_html = df_html.head(500)
    return df_html


def clean_lists_columns(alert_value):
    """Clean the columns that are lists."""
    if alert_value == "['-']":
        return 0
    try:
        return len(literal_eval(alert_value))
    except (SyntaxError, ValueError):
        return 0


def clean_medicinal_columns(med_value, rules=True, sascore=False):
    if rules:
        if med_value == 0:
            return 'Accepted'
        else:
            return 'Rejected'
    else:
        if sascore:
            if med_value < 6:
                return 'Easy'
            else:
                return 'Hard'
        else:
            if med_value == 0:
                return 'Easy'
            else:
                return 'Hard'


def get_toxicity_score(input_df):
    toxicity = input_df.columns[62:86]
    toxicity_region_dropped = input_df[toxicity].drop(columns=['IGC50', 'LC50DM', 'LC50FM', 'BCF', 'EC'], axis=1)
    input_df['mean_toxicity'] = toxicity_region_dropped.mean(axis=1)
    input_df['std_toxicity'] = toxicity_region_dropped.std(axis=1)
    input_df['toxicity_score'] = (input_df['mean_toxicity'] + input_df['std_toxicity']) / 2
    input_df = input_df.drop(columns=['mean_toxicity', 'std_toxicity'], axis=1)
    return input_df


def get_medicinal_score(input_df):
    input_df['qed_score'] = input_df['QED'].apply(lambda x: 0.15 if x > 0.67 else 0.85)
    input_df['gasa_score'] = input_df['gasa'].apply(lambda x: 0.15 if x == 'Easy' else 0.85)
    input_df['sascore_score'] = input_df['SA-score'].apply(lambda x: 0.15 if x == 'Easy' else 0.85)
    input_df['fsp3_score'] = input_df['Fsp3'].apply(lambda x: 0.15 if x >= 0.42 else 0.85)
    input_df['mce18_score'] = input_df['MCE-18'].apply(lambda x: 0.15 if x >= 45 else 0.85)
    input_df['alarmnmr_score'] = input_df['Alarm_NMR'].apply(lambda x: 0.15 if x == "['-']" else 0.85)
    input_df['bms_score'] = input_df['BMS'].apply(lambda x: 0.15 if x == "['-']" else 0.85)
    input_df['pains_score'] = input_df['PAINS'].apply(lambda x: 0.15 if x == "['-']" else 0.85)
    input_df['chelating_score'] = input_df['Chelating'].apply(lambda x: 0.15 if x == "['-']" else 0.85)
    input_df['pfizer_score'] = input_df['Pfizer'].apply(lambda x: 0.15 if x == 'Accepted' else 0.85)
    input_df['lipinski_score'] = input_df['Lipinski'].apply(lambda x: 0.15 if x == 'Accepted' else 0.85)
    input_df['gsk_score'] = input_df['GSK'].apply(lambda x: 0.15 if x == 'Accepted' else 0.85 * 2)
    input_df['goldentriangle_score'] = input_df['GoldenTriangle'].apply(lambda x: 0.15 if x == 'Accepted' else 0.85 * 2)
    new_score_columns = ['qed_score', 'gasa_score', 'sascore_score', 'fsp3_score', 'mce18_score', 'alarmnmr_score',
                         'bms_score', 'pains_score', 'chelating_score', 'pfizer_score', 'lipinski_score', 'gsk_score',
                         'goldentriangle_score']
    columns_to_change = ['Aggregators', 'Fluc', 'Blue_fluorescence', 'Green_fluorescence', 'Reactive', 'Promiscuous']
    for column in columns_to_change:
        input_df[column] = input_df[column].astype(float)
    weights = {
        'pfizer_score': 10,
        'sascore_score': 10,
        'lipinski_score': 5,
        'gsk_score': 2,
        'goldentriangle_score': 1
    }

    for score, weight in weights.items():
        input_df[score + '_weighted'] = input_df[score] * weight

    weights_sum = sum(weights.values())
    input_df['medicinal_score'] = input_df[[score + '_weighted' for score in weights.keys()]].sum(axis=1) / weights_sum
    input_df = input_df.drop(columns=[score + '_weighted' for score in weights.keys()], axis=1)
    input_df.drop(columns=new_score_columns, axis=1, inplace=True)

    return input_df


def get_absortion_score(input_df):
    absortion = input_df.columns[21:30]
    input_df['caco2_score'] = input_df['caco2'].apply(lambda x: 0.15 if x > -5.15 else 0.85)
    absortion_score = pd.concat([input_df[absortion], input_df['caco2_score']], axis=1)
    absortion_score = absortion_score.drop(columns=['caco2', 'MDCK'], axis=1)
    input_df['absortion_score'] = absortion_score.mean(axis=1)
    input_df = input_df.drop(columns=['caco2_score'], axis=1)
    return input_df


def get_distribution_score(input_df):
    distribution = input_df.columns[30:39]
    input_df['logvdss_score'] = input_df['logVDss'].apply(lambda x: 0.15 if 0.04 < x < 20 else 0.85)
    input_df['ppb_score'] = input_df['PPB'].apply(lambda x: 0.15 if x <= 90.0 else 0.85)
    input_df['fu_score'] = input_df['Fu'].apply(lambda x: 0.15 if x > 5.0 else 0.85)
    distribution_score = pd.concat([input_df[distribution], input_df[['logvdss_score', 'ppb_score', 'fu_score']]],
                                   axis=1)
    distribution_score = distribution_score.drop(columns=['logVDss', 'PPB', 'Fu'], axis=1)
    input_df['distribution_score'] = distribution_score.mean(axis=1)
    input_df = input_df.drop(columns=['logvdss_score', 'ppb_score', 'fu_score'], axis=1)
    return input_df


def get_metabolism_score(input_df):
    metabolism = input_df.columns[39:53]
    input_df['lmhuman_score'] = input_df['LM-human'].apply(lambda x: 1 - x)
    metabolism_score = pd.concat([input_df[metabolism], input_df['lmhuman_score']], axis=1)
    metabolism_score = metabolism_score.drop(columns=['LM-human'], axis=1)
    input_df['metabolism_score'] = metabolism_score.mean(axis=1)
    input_df = input_df.drop(columns=['lmhuman_score'], axis=1)
    return input_df


def get_excretion_score(input_df):
    input_df['clplasma_score'] = input_df['cl-plasma'].apply(
        lambda x: 0.15 if 0 < x <= 5 else (0.5 if 5 < x <= 15 else 0.85))
    input_df['t0.5_score'] = input_df['t0.5'].apply(lambda x: 0.15 if x > 8 else (0.5 if 1 < x <= 8 else 0.85))
    excretion_score = input_df[['clplasma_score', 't0.5_score']]
    input_df['excretion_score'] = excretion_score.mean(axis=1)
    input_df = input_df.drop(columns=['clplasma_score', 't0.5_score'], axis=1)
    return input_df


def get_tox21_score(input_df):
    tox21 = input_df.columns[86:98]
    tox21_score = input_df[tox21]
    input_df['tox21_score'] = tox21_score.mean(axis=1)
    return input_df


def get_pharmisa_score(input_df):
    weights = {
        'toxicity_score': 20,
        'medicinal_score': 15,
        'absortion_score': 3,
        'distribution_score': 2.5,
        'metabolism_score': 2,
        'excretion_score': 1,
        'tox21_score': 1
    }

    for score, weight in weights.items():
        input_df[score + '_weighted'] = input_df[score] * weight

    weights_sum = sum(weights.values())  # A soma dos pesos
    input_df['Pharmisa Score'] = input_df[[score + '_weighted' for score in weights.keys()]].sum(axis=1) / weights_sum
    input_df = input_df.drop(columns=[score + '_weighted' for score in weights.keys()], axis=1)
    return input_df


def results_to_html(output_folder_path: str, folder_name: str):
    """Converts the results to a html file"""
    global df_old
    df_old = pd.read_csv(f"{output_folder_path}/results/admet_filtered.csv")
    define_globals(df_old)
    subtitle = None
    if len(df_old) > 500:
        subtitle = f"<h4>The results shown are limited to 500. Total results: {len(df_old)}.</h4>"
    df_html = get_df_html(df_old)
    df_html = df_html.round(3)
    for col in df_html.columns:
        df_html[col] = df_html[col].apply(lambda x: '{:.3f}'.format(x) if isinstance(x, (int, float)) else x)
    styled_html_df = df_html.style.apply(color_format, axis=0)
    html = styled_html_df.to_html(index=False)
    html = """
    <head>
        <link rel='preconnect' href='https://fonts.googleapis.com'>
        <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
        <link href='https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap' rel='stylesheet'>
        <style>
            body {
                font-family: 'Lato', sans-serif;
            }
        </style>
    </head>
    """ + html
    if subtitle:
        html = subtitle + html
    with open(f"{output_folder_path}/results/{folder_name}_results.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    results_to_html("/home/kdunorat/lambdapipe_results/7KR1-3-CID87", "novosparam")
