import pandas as pd


def color_format(column):
    """Color formatting for the DataFrame."""
    column_name = column.name
    if column_name in ['SMILES', 'Molecule ID', 'Score Pharmit', 'RMSD Pharmit']:
        return ['background-color: default' for _ in column]
    if column_name == 'SA-score':
        color = column.apply(lambda val: '#2e7d32' if val < 6 else '#b71c1c')
    elif column_name in ['Lipinski', 'Pfizer', 'GSK', 'GoldenTriangle']:
        color = column.apply(lambda val: '#2e7d32' if val == 'Accepted' else '#b71c1c')
    else:
        color = column.apply(lambda val: '#2e7d32' if 0 <= val <= 0.3 else ('#ffeb3b' if 0.3 < val <= 0.7 else '#b71c1c'))

    color = color.apply(lambda val: f'background-color: {val}' if isinstance(val, str) else 'background-color: default')
    return color


def calculate_score(row):
    sa_score = row['SA-score']
    pfizer = row['Pfizer']
    mean_toxicity = row['mean_toxicity']
    std_toxicity = row['std_toxicity']
    rules_score = row['rules_score']

    # Give more weight to 'SA-score' and 'Pfizer'
    pfizer_weight = 3 if pfizer == 1 else 1
    rules_weight = 7.5

    # Decrease the score as the toxicity decreases
    toxicity_score = 2 / (mean_toxicity + std_toxicity)

    score = (sa_score + pfizer_weight * pfizer + rules_score * rules_weight) - toxicity_score
    return score


def get_df_html(df_html_old: pd.DataFrame):
    first_column = df_html_old.iloc[:, 0]
    rules = df_html_old.iloc[:, 30:35]
    toxicity = df_html_old.iloc[:, 2:12]
    df_html = pd.concat([first_column, toxicity, rules], axis=1)
    df_html['mean_toxicity'] = toxicity.mean(axis=1)
    df_html['std_toxicity'] = toxicity.std(axis=1)
    df_html['rules_score'] = df_html['Lipinski'] + df_html['Pfizer'] + df_html['GSK'] + df_html['GoldenTriangle']
    df_html['score'] = df_html.apply(calculate_score, axis=1)
    df_html['Score Pharmit'] = df_html_old['Score Pharmit']
    df_html['RMSD Pharmit'] = df_html_old['RMSD Pharmit']
    df_html['SMILES'] = df_html_old['SMILES']
    df_html = df_html.sort_values(by='score', ascending=True)
    df_html = df_html.reset_index(drop=True)
    df_html = df_html.drop(columns=['mean_toxicity', 'std_toxicity', 'score', 'rules_score'])
    rules_columns = ['Lipinski', 'Pfizer', 'GSK', 'GoldenTriangle']
    df_html[rules_columns] = df_html[rules_columns].replace({0: 'Accepted', 1: 'Rejected'})
    if len(df_html) > 500:
        df_html = df_html.head(500)
    return df_html


def results_to_html(output_folder_path: str, folder_name: str):
    """Converts the results to a html file"""
    df = pd.read_csv(f"{output_folder_path}/results/admet_filtered.csv")
    df_html = get_df_html(df)
    styled_html_df = df_html.style.apply(color_format, axis=0)
    html = styled_html_df.to_html(index=False)
    if len(df_html) > 500:
        subtitle = "<h4>Only the top 500 molecules are shown</h4>"
        html = subtitle + html
    with open(f"{output_folder_path}/results/{folder_name}_results.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    results_to_html("/home/kdunorat/lambdapipe_results/7DK5-272", "newww")
